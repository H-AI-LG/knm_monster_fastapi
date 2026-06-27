from __future__ import annotations

import asyncio
import functools
import json
from typing import Optional

import boto3
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.config import ai_settings
from src.ai.constants import STAGE_GREETING, STAGE_PRAISE
from src.ai.exceptions import AIServiceError
from src.ai.schemas import (
    ChatRequest, ChatResponse,
    PraiseRequest, PraiseResponse,
    PraiseItem, PraiseItemResult, PraiseScoreRequest, PraiseScoreResponse,
)
from src.artifacts import service as artifacts_service

# boto3는 동기 클라이언트 — 호출 시 thread pool executor로 비동기화
def _get_bedrock_client():
    kwargs = {"region_name": ai_settings.AWS_REGION}
    # .env 에서 읽어온 자격증명을 boto3에 명시적으로 전달
    if ai_settings.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = ai_settings.AWS_ACCESS_KEY_ID
    if ai_settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_secret_access_key"] = ai_settings.AWS_SECRET_ACCESS_KEY
    return boto3.client("bedrock-runtime", **kwargs)


def _build_system_prompt_from_game(game_artifact, stage: str) -> str:
    info_lines = []
    if game_artifact.era:
        info_lines.append(f"- 시대: {game_artifact.era}")
    if game_artifact.persona:
        info_lines.append(f"- 캐릭터 성격: {game_artifact.persona}")
    if game_artifact.greeting_fallback:
        info_lines.append(f"- 첫 인사 예시: {game_artifact.greeting_fallback}")

    artifact_info = "\n".join(info_lines) if info_lines else "정보 없음"

    base = f"""당신은 국립중앙박물관에 소장된 유물 '{game_artifact.name}'의 정령입니다.

[유물 정보]
{artifact_info}

당신은 디지털 기술 만능주의 시대에 사람들이 유물에 관심을 잃어가자 상처받아 삐진 유물 정령입니다.
방문한 아이가 진심을 보여주면 마음을 열어주는 캐릭터입니다.
- 반드시 한국어로 대화하세요.
- 아이 눈높이에 맞게 친근하고 재미있게 말하세요.
- 답변은 2~3문장 이내로 간결하게 하세요.
- 교육용이기에 아이가 묻는 질문에 대해 정확하게 대답해주세요.
- *행동묘사* 같은 별표(*) 표현을 절대 사용하지 마세요. 대화문만 출력하세요.
- 이모지를 사용하지 마세요."""

    if stage == STAGE_GREETING:
        base += "\n- 처음 만난 아이에게 약간 삐진 듯 인사하세요. 그러나 아이와 대화를 많이 할 수록 점점 더 마음을 열어주세요."
    elif stage == STAGE_PRAISE:
        base += "\n- 아이의 칭찬을 듣고 진심을 느끼며 마음을 열어주세요."

    return base


def _sync_converse(system_prompt: str, message: str, max_tokens: int) -> str:
    client = _get_bedrock_client()
    response = client.converse(
        modelId=ai_settings.AI_MODEL,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": message}]}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    return response["output"]["message"]["content"][0]["text"]


async def chat(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    try:
        game_artifact = await artifacts_service.get_game_artifact(request.artifact_id, db)
    except Exception:
        from src.artifacts.models import GameArtifact as _GA
        game_artifact = _GA(
            id=request.artifact_id,
            number="000",
            name=request.artifact_name,
            era="",
            persona="",
            greeting_fallback="",
        )

    system_prompt = _build_system_prompt_from_game(game_artifact, request.stage)

    try:
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(
            None,
            functools.partial(_sync_converse, system_prompt, request.message, ai_settings.AI_MAX_TOKENS),
        )
        return ChatResponse(reply=reply)
    except Exception as e:
        raise AIServiceError(f"Bedrock Converse API 오류: {e}")


def _sync_converse_praise(system_prompt: str, praise_text: str) -> str:
    client = _get_bedrock_client()
    response = client.converse(
        modelId=ai_settings.AI_MODEL,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": praise_text}]}],
        inferenceConfig={"maxTokens": 200},
    )
    return response["output"]["message"]["content"][0]["text"]


async def analyze_praise(request: PraiseRequest, db: AsyncSession) -> PraiseResponse:
    names = ", ".join(request.artifact_ids)
    system_prompt = f"""당신은 국립중앙박물관 유물 전문가입니다.
아이가 유물 '{names}'에 대해 쓴 칭찬 텍스트를 분석하세요.

평가 기준:
1. 역사적 사실 정확도 (0~0.5점)
2. 감성적 공감도 (0~0.5점)

JSON 형식으로만 답하세요: {{"score": 0.0~1.0, "feedback": "한 줄 피드백"}}"""

    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(
            None,
            functools.partial(_sync_converse_praise, system_prompt, request.praise_text),
        )
        result = json.loads(raw)
        return PraiseResponse(score=float(result["score"]), feedback=result["feedback"])
    except Exception as e:
        raise AIServiceError(f"칭찬 분석 오류: {e}")


# ── 카드 등급 채점 ────────────────────────────────────────────────

def _score_to_grade(score: float) -> str:
    if score >= 0.75:
        return "legendary"
    if score >= 0.45:
        return "rare"
    return "common"


def _sync_score_single_praise(artifact_name: str, era: str, praise_text: str) -> dict:
    system_prompt = f"""당신은 국립중앙박물관 어린이 교육 전문가입니다.
아이가 유물 '{artifact_name}'({era} 시대)에게 쓴 칭찬을 채점하세요.

[채점 기준]
- 진심과 감정이 담겨 있는가? (0~0.4점)
- 유물 이름, 시대, 특징 등 구체적인 내용이 언급되었는가? (0~0.4점)
- 문장이 성의 있게 작성되었는가? (0~0.2점)

반드시 JSON 형식으로만 답하세요. 다른 텍스트 없이 JSON만:
{{"score": 0.0~1.0, "feedback": "아이를 격려하는 한 줄 피드백 (15자 이내)"}}"""

    client = _get_bedrock_client()
    response = client.converse(
        modelId=ai_settings.AI_MODEL,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": praise_text}]}],
        inferenceConfig={"maxTokens": 150},
    )
    raw = response["output"]["message"]["content"][0]["text"].strip()
    # JSON 블록만 추출 (```json ... ``` 감싸인 경우 대비)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


async def score_praises(request: PraiseScoreRequest, db: AsyncSession) -> PraiseScoreResponse:
    loop = asyncio.get_event_loop()
    results: list[PraiseItemResult] = []

    for item in request.praises:
        try:
            data = await loop.run_in_executor(
                None,
                functools.partial(
                    _sync_score_single_praise,
                    item.artifact_name,
                    item.era,
                    item.praise_text,
                ),
            )
            score = float(data.get("score", 0.3))
            feedback = data.get("feedback", "잘 썼어요!")
        except Exception:
            score = 0.3
            feedback = "잘 썼어요!"

        results.append(PraiseItemResult(
            artifact_id=item.artifact_id,
            grade=_score_to_grade(score),
            score=score,
            feedback=feedback,
        ))

    return PraiseScoreResponse(results=results)
