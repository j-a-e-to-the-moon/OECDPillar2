from pydantic import BaseModel, Field
from typing import Optional, Union
from decimal import Decimal
from enum import Enum

class EntityType(str, Enum):
    PARENT = "parent"
    SUBSIDIARY = "subsidiary"
    JOINT_VENTURE = "joint_venture"
    BRANCH = "branch"

class NullableEntity(BaseModel):
    """Nullable 필드 사용 예시"""
    
    # 1. 필수 필드 (C#의 [Required])
    name: str = Field(..., description="법인명 - 필수")
    country: str = Field(..., description="국가 - 필수")
    revenue: Decimal = Field(..., ge=0, description="수익 - 필수")
    
    # 2. Optional 필드 (C#의 nullable) - 방법 1
    description: Optional[str] = Field(None, description="설명 - 선택적 (null 가능)")
    tax_credit: Optional[Decimal] = Field(None, description="세액공제 - 선택적 (null 가능)")
    
    # 3. Optional 필드 - 방법 2 (Python 3.10+ 문법)
    # notes: str | None = Field(None, description="메모 - 선택적")
    
    # 4. 기본값이 있는 선택적 필드
    entity_type: EntityType = Field(default=EntityType.SUBSIDIARY, description="법인 유형 - 기본값 있음")
    employees: int = Field(default=0, ge=0, description="직원 수 - 기본값 0")
    
    # 5. Optional + 기본값 조합
    tax_rate: Optional[Decimal] = Field(default=Decimal('0.15'), description="세율 - 기본값 15%")
    
    # 6. 완전히 선택적 (None 허용, 기본값 None)
    parent_company: Optional[str] = Field(default=None, description="모회사명 - 완전 선택적")
    
    # 7. 리스트도 nullable 가능
    subsidiaries: Optional[list[str]] = Field(default=None, description="자회사 목록 - 선택적")

# 실제 사용 예시들
class ValidationExamples(BaseModel):
    """다양한 nullable 검증 패턴"""
    
    # 필수이지만 빈 문자열 허용 안함
    required_non_empty: str = Field(..., min_length=1, description="필수이고 비어있으면 안됨")
    
    # 선택적이지만 값이 있으면 비어있으면 안됨
    optional_non_empty: Optional[str] = Field(None, min_length=1, description="선택적이지만 값이 있으면 비어있으면 안됨")
    
    # 숫자 범위 + nullable
    optional_percentage: Optional[Decimal] = Field(None, ge=0, le=1, description="선택적 비율 (0-1)")
    
    # 조건부 필수 (다른 필드에 따라)
    joint_venture_name: Optional[str] = Field(None, description="합작투자 이름")
    joint_venture_percentage: Optional[Decimal] = Field(None, ge=0, le=1, description="합작투자 지분율")

# 실제 사용법 비교
def usage_examples():
    """사용법 예시"""
    
    # 1. 최소한의 필수 필드만
    entity1 = NullableEntity(
        name="삼성전자",
        country="한국",
        revenue=Decimal('1000000')
        # description, tax_credit 등은 None으로 자동 설정
    )
    
    # 2. 일부 선택적 필드 포함
    entity2 = NullableEntity(
        name="LG전자",
        country="한국", 
        revenue=Decimal('800000'),
        description="전자제품 제조업체",  # Optional 필드에 값 제공
        tax_credit=Decimal('5000'),      # Optional 필드에 값 제공
        employees=1000                    # 기본값 대신 명시적 값
    )
    
    # 3. None 값 명시적 설정
    entity3 = NullableEntity(
        name="스타트업",
        country="한국",
        revenue=Decimal('50000'),
        description=None,           # 명시적으로 None
        tax_credit=None,           # 명시적으로 None
        parent_company=None        # 명시적으로 None
    )

# JSON 직렬화 시 None 처리
class SerializationSettings(BaseModel):
    """직렬화 설정 예시"""
    name: str
    optional_field: Optional[str] = None
    
    class Config:
        # None 값을 JSON에서 제외하고 싶을 때
        exclude_none = True  # None 값은 JSON에서 제외됨
        
        # 또는 None을 명시적으로 포함하고 싶을 때는 이 설정을 사용하지 않음 