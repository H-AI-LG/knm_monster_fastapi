from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.users.models import User
from src.users.schemas import LoginRequest
from src.artifacts.models import Artifact
from sqlalchemy import or_

async def authenticate_or_register_user(db: AsyncSession, login_data: LoginRequest):
    
    query = select(User).where(
        User.name == login_data.name, 
        User.parent_phone == login_data.parent_phone
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            name=login_data.name,
            parent_phone=login_data.parent_phone,
            parent_email=login_data.parent_email, 
            interests=login_data.interests,      
            view_time=login_data.view_time   
        )
        db.add(user)
        await db.commit()      # DB에 실제 저장
        await db.refresh(user) # 저장된 유저 정보(자동 생성된 id 포함) 동기화
        print(f"✨ 신규 학생 등록 및 자동 회원가입 완료: {user.name}")
    
    # 기존에 있던 유저 로그인 시, 추가 정보가 있으면 업데이트
    else:
        if login_data.parent_email is not None:
            user.parent_email = login_data.parent_email
        if login_data.interests is not None:
            user.interests = login_data.interests
        if login_data.view_time is not None:
            user.view_time = login_data.view_time
            
        await db.commit()
        await db.refresh(user)
        print(f"👋 기존 학생 로그인 및 정보 업데이트 완료: {user.name}")

    return user

async def get_recommended_artifacts(db: AsyncSession, user_interests: str, limit_count: int = 5):
    """
    사용자의 관심사 키워드를 받아서 연관된 유물을 추천해주는 함수
    """
    
    # mock_artifacts = [
    #     {"id": 1, "title": "청자 매병", "subdescription": "도자기"},
    #     {"id": 2, "title": "백자 항아리", "subdescription": "도자기"},
    #     {"id": 3, "title": "사인검", "subdescription": "전쟁, 무기"}
    # ]
    
    interest_list = [keyword.strip() for keyword in user_interests.split(",") if keyword.strip()]
    
    # 만약 관심사가 없다면? 기본적으로 아무 유물이나 최신순/랜덤으로 가져옵니다.
    if not interest_list:
        query = select(Artifact).limit(limit_count)
        result = await db.execute(query)
        return result.scalars().all()

    conditions = []
    for keyword in interest_list:
        conditions.append(Artifact.subdescription.like(f"%{keyword}%"))
        conditions.append(Artifact.subject_keyword.like(f"%{keyword}%"))

    # 관심사 키워드 중 하나라도 포함된 유물을 가져오는 쿼리
    query = select(Artifact).where(or_(*conditions)).limit(limit_count)
    
    # 4. DB 실행 후 결과 리턴
    result = await db.execute(query)
    return result.scalars().all()
    # recommended = []
    # for art in mock_artifacts:
    #     for keyword in interest_list:
    #         if keyword in art["subdescription"]:
    #             recommended.append(art)
    #             break # 중복 방지
                
    # return recommended[:limit_count]