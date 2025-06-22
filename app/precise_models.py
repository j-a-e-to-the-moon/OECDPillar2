from decimal import Decimal, ROUND_HALF_UP, getcontext
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

# 정밀도 설정
DECIMAL_PLACES = 10  # 소수점 10자리까지
getcontext().prec = 28  # 높은 정밀도 설정

class EntityType(str, Enum):
    """법인 유형"""
    PARENT = "parent"
    SUBSIDIARY = "subsidiary"
    JOINT_VENTURE = "joint_venture"
    BRANCH = "branch"

class PreciseEntity(BaseModel):
    """정교한 계산을 위한 법인 정보 (Decimal 사용)"""
    name: str = Field(..., description="법인명")
    country: str = Field(..., description="국가")
    entity_type: EntityType = Field(..., description="법인 유형")
    revenue: Decimal = Field(..., ge=0, description="수익")
    profit: Decimal = Field(..., description="이익")
    tax_paid: Decimal = Field(..., ge=0, description="납부한 세금")
    employees: int = Field(..., ge=0, description="직원 수")
    
    @validator('revenue', 'profit', 'tax_paid')
    def round_decimal_values(cls, v):
        """Decimal 값을 지정된 자릿수로 반올림"""
        if isinstance(v, Decimal):
            return v.quantize(Decimal('0.' + '0' * DECIMAL_PLACES), rounding=ROUND_HALF_UP)
        return Decimal(str(v)).quantize(Decimal('0.' + '0' * DECIMAL_PLACES), rounding=ROUND_HALF_UP)

class HighPrecisionEntity(BaseModel):
    """최고 정밀도 계산을 위한 법인 정보 (Decimal 사용)"""
    name: str = Field(..., description="법인명")
    country: str = Field(..., description="국가")
    entity_type: EntityType = Field(..., description="법인 유형")
    revenue: Decimal = Field(..., ge=0, description="수익 (최고 정밀도)")
    profit: Decimal = Field(..., description="이익 (최고 정밀도)")
    tax_paid: Decimal = Field(..., ge=0, description="납부한 세금 (최고 정밀도)")
    employees: int = Field(..., ge=0, description="직원 수")
    
    @validator('revenue', 'profit', 'tax_paid')
    def round_decimal_values(cls, v):
        """Decimal 값을 지정된 자릿수로 반올림"""
        if isinstance(v, Decimal):
            return v.quantize(Decimal('0.' + '0' * DECIMAL_PLACES), rounding=ROUND_HALF_UP)
        return Decimal(str(v)).quantize(Decimal('0.' + '0' * DECIMAL_PLACES), rounding=ROUND_HALF_UP)

# 요청/응답 모델들 (Decimal 기반)
class PreciseEffectiveTaxRateRequest(BaseModel):
    """정교한 유효세율 계산 요청"""
    entities: List[PreciseEntity] = Field(..., description="법인 목록")
    minimum_tax_rate: Decimal = Field(default=Decimal('0.15'), ge=0, le=1, description="최소세율 (기본값: 15%)")

class PreciseEffectiveTaxRateResponse(BaseModel):
    """정교한 유효세율 계산 응답"""
    entity_name: str = Field(..., description="법인명")
    effective_tax_rate: Decimal = Field(..., description="유효세율")
    is_low_taxed: bool = Field(..., description="저세율 여부")
    additional_tax_required: Decimal = Field(..., description="추가 납부 세금")

class PreciseIncomeInclusionRequest(BaseModel):
    """정교한 소득 포함 비율 계산 요청"""
    low_taxed_income: Decimal = Field(..., ge=0, description="저세율 소득")
    total_income: Decimal = Field(..., ge=0, description="총 소득")
    ownership_percentage: Decimal = Field(..., ge=0, le=1, description="지분율")

class PreciseIncomeInclusionResponse(BaseModel):
    """정교한 소득 포함 비율 계산 응답"""
    inclusion_ratio: Decimal = Field(..., description="소득 포함 비율")
    taxable_amount: Decimal = Field(..., description="과세 대상 금액")

# 계산 유틸리티 함수들
class PrecisionCalculator:
    """정교한 계산을 위한 유틸리티 클래스"""
    
    @staticmethod
    def calculate_effective_tax_rate_decimal(entity: PreciseEntity) -> Decimal:
        """Decimal을 사용한 유효세율 계산"""
        if entity.profit <= 0:
            return Decimal('0')
        return (entity.tax_paid / entity.profit).quantize(
            Decimal('0.' + '0' * DECIMAL_PLACES), 
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_effective_tax_rate_high_precision(entity: HighPrecisionEntity) -> Decimal:
        """최고 정밀도 Decimal을 사용한 유효세율 계산"""
        if entity.profit <= 0:
            return Decimal('0')
        return (entity.tax_paid / entity.profit).quantize(
            Decimal('0.' + '0' * DECIMAL_PLACES), 
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_additional_tax_decimal(entity: PreciseEntity, minimum_rate: Decimal) -> Decimal:
        """Decimal을 사용한 추가 납부 세금 계산"""
        if entity.profit <= 0:
            return Decimal('0')
        
        effective_rate = PrecisionCalculator.calculate_effective_tax_rate_decimal(entity)
        if effective_rate >= minimum_rate:
            return Decimal('0')
        
        required_tax = entity.profit * minimum_rate
        additional_tax = required_tax - entity.tax_paid
        return max(Decimal('0'), additional_tax).quantize(
            Decimal('0.' + '0' * DECIMAL_PLACES), 
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_ownership_ratio(direct_ownership: Decimal, indirect_ownership: Decimal) -> Decimal:
        """직간접 지분 비율 계산"""
        total_ownership = direct_ownership + indirect_ownership
        return total_ownership.quantize(
            Decimal('0.' + '0' * DECIMAL_PLACES), 
            rounding=ROUND_HALF_UP
        )

# 정밀도 비교를 위한 예시 클래스
class PrecisionComparison(BaseModel):
    """다양한 정밀도 타입 비교"""
    value_float: float = Field(..., description="기본 float")
    value_decimal: Decimal = Field(..., description="Decimal (정확)")
    value_high_precision: Decimal = Field(..., description="고정밀 Decimal (최고 정밀도)")
    
    @validator('value_decimal', 'value_high_precision')
    def round_decimal_values(cls, v):
        """Decimal 값을 지정된 자릿수로 반올림"""
        if isinstance(v, Decimal):
            return v.quantize(Decimal('0.' + '0' * DECIMAL_PLACES), rounding=ROUND_HALF_UP)
        return Decimal(str(v)).quantize(Decimal('0.' + '0' * DECIMAL_PLACES), rounding=ROUND_HALF_UP) 