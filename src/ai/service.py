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
from src.ai.schemas import ChatRequest, ChatResponse, PraiseRequest, PraiseResponse
from src.artifacts import service as artifacts_service
from src.artifacts.schemas import ArtifactDB

# boto3는 동기 클라이언트 — 호출 시 thread pool executor로 비동기화
def _get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=ai_settings.AWS_REGION)


def _build_system_prompt(artifact: ArtifactDB, stage: str) -> str:
    info_lines = []
    if artifact.temporal:
        info_lines.append(f"- 시대: {artifact.temporal}")
    if artifact.medium:
        info_lines.append(f"- 재질: {artifact.medium}")
    if artifact.extent:
        info_lines.append(f"- 크기: {artifact.extent}")
    if artifact.spatial:
        info_lines.append(f"- 출토/소장지: {artifact.spatial}")
    if artifact.subdescription:
        info_lines.append(f"- 분류: {artifact.subdescription}")
    if artifact.description:
        info_lines.append(f"- 설명: {artifact.description}")

    artifact_info = "\n".join(info_lines) if info_lines else "정보 없음"

    base = f"""당신은 국립중앙박물관에 소장된 유물 '{artifact.title}'의 정령입니다.

[유물 정보]
{artifact_info}

당신은 디지털 기술 만능주의 시대에 사람들이 스마트폰만 보고 박물관을 찾지 않자 상처받아 삐진 유물 정령입니다.
방문한 아이가 진심을 보여주면 마음을 열어주는 캐릭터입니다.
- 반드시 한국어로 대화하세요.
- 아이 눈높이에 맞게 친근하고 재미있게 말하세요.
- 답변은 2~3문장 이내로 간결하게 하세요."""

    if stage == STAGE_GREETING:
        base += "\n- 처음 만난 아이에게 약간 삐진 듯 인사하세요."
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
        artifact = await artifacts_service.get_by_name(request.artifact_name, db)
        artifact_schema = artifacts_service.to_schema(artifact)
    except Exception:
        artifact_schema = ArtifactDB(
            id=0,
            title=request.artifact_name,
            description="",
            subdescription="",
            temporal="",
            spatial="",
            medium="",
            extent="",
            url="",
        )

    system_prompt = _build_system_prompt(artifact_schema, request.stage)

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
