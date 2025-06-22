from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
from enum import Enum
import numpy as np


# OECD Pillar2 관련 모델들

class UltimateParentEntityAccountingType(str, Enum):
    """Ultimate Parent Entity Accounting Type"""
    ULTIMATE_PARENT_ENTITY = "ultimate_parent_entity"
    CONSOLIDATED = "consolidated"
    EQUITY_METHOD = "equity_method"
    ETC = "etc"

class ParentEntityType(str, Enum):
    """Parent Entity Type"""
    ULTIMATE_PARENT_ENTITY = "ultimate_parent_entity"
    PARTIALLY_OWNED_PARENT_ENTITY = "partially_owned_parent_entity"
    INTERMEDIATE_PARENT_ENTITY = "intermediate_parent_entity"

class SafeharboursGroup(BaseModel):
    HASHCODE: str = Field(..., description="the hashcode of the safeharbours group, primary key")
    jurisdiction: str = Field(..., description="the jurisdiction that constitutes the basic unit of effective tax rate calculation")
    joint_venture_group_top_company_name: Optional[str] = Field(None, description="the name of the joint venture group top company")

class EffectiveTaxRateCalculationGroup(BaseModel):
    HASHCODE: str = Field(..., description="the hashcode of the effective tax rate calculation group, primary key")
    jurisdiction: str = Field(..., description="the jurisdiction that constitutes the basic unit of effective tax rate calculation")
    is_stateless_entity_group: bool = Field(..., description="the stateless entity group")
    is_investment_entity_group: bool = Field(..., description="the investment entity group, primary key")
    minority_owned_group_top_company_name: Optional[str] = Field(None, description="the name of the minority owned group top company")
    joint_venture_group_top_company_name: Optional[str] = Field(None, description="the name of the joint venture group top company")

class EntityRequest(BaseModel):
    """Entity Information Request"""
    name: str = Field(..., description="the name of the entity, primary key")
    jurisdiction: str = Field(..., description="the jurisdiction that constitutes the basic unit of effective tax rate calculation")
    ultimate_parent_entity_accounting_type: UltimateParentEntityAccountingType = Field(..., description="the accounting type of the ultimate parent entity")
    is_investment_entity: Optional[bool] = Field(default=False, description="the investment entity, default value is False")
    is_flow_through_entity: Optional[bool] = Field(default=False, description="the flow through entity, default value is False")
    is_untaxed_permanent_establishment: Optional[bool] = Field(default=False, description="the untaxed permanent establishment, default value is False")
    is_excluded_entity: Optional[bool] = Field(default=False, description="the excluded entity, default value is False")
    is_excluded_from_safeharbours: Optional[bool] = Field(default=False, description="the excluded from safeharbours, default value is False")
    direct_controller_name: Optional[str] = Field(default="etc", description="the direct controller name, default value is 'etc'")
    precedence_order_in_org_chart: Optional[int] = Field(None, description="the precedence order in the org chart, default value is None, when duplicate, the order is granted automatically by the system among the same level")

class OwnershipRequest(BaseModel):
    """Ownership Information Request"""
    owner_entity_name: str = Field(..., description="the name of the owner entity")
    owned_entity_name: str = Field(..., description="the name of the owned entity")
    ownership_percentage: np.float128 = Field(..., ge=0, le=1, description="the ownership percentage")

class CompanyResponse(BaseModel):
    """Pillar2 Calculation Structure Response for Company"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    parent_entity_type: Optional[ParentEntityType] = Field(None, description="the type of the parent entity, when it is not a parent entity, it is None")
    safeharbours_group: Optional[str] = Field(None, description="the name of the safeharbours group, when it is excluded entity in calculating safe harbours, it is None")
    effective_tax_rate_calculation_group: Optional[str] = Field(None, description="the name of the effective tax rate calculation group, when it is excluded entity in calculating effective tax rate, it is None")
    income_inclusion_rule_taxed_ratio: np.float128 = Field(default=0, ge=0, le=1, description="the taxed ratio of the income inclusion rule, when it is not taxed by IIR, it is 0")
    utpr_taxed_ratio: np.float128 = Field(default=0, ge=0, le=1, description="the taxed ratio of the undertaxed payments rule, when it is not taxed by UTPR, it is 0")

class IncomeInclusionRuleResponse(BaseModel):
    """Income Inclusion Rule Response"""
    parent_entity_name: str = Field(..., description="the name of the parent entity, primary key")
    owned_entity_names: List[str] = Field(..., description="the names of the owned entities")
    direct_indirect_ownership_ratio: np.float128 = Field(default=0, ge=0, le=1, description="the ratio of the direct and indirect ownership, when it is not owned by the parent entity, it is 0")
    income_inclusion_ratio: np.float128 = Field(default=0, ge=0, le=1, description="the ratio of the income inclusion, when it is not included by IIR, it is 0")
    
    @property
    def offset_ratio(self) -> np.float128:
        return self.direct_indirect_ownership_ratio - self.income_inclusion_ratio

class UnderTaxedPaymentsRuleResponse(BaseModel):
    """Under Taxed Payments Rule Response"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    utpr_taxed_ratio: np.float128 = Field(default=0, ge=0, le=1, description="the ratio of the undertaxed payments rule, when it is not taxed by UTPR, it is 0")

class OrgChartResponse(BaseModel):
    """Org Chart Response"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    node_location: Tuple[int,int] = Field(..., description="the location of the node in the org chart, the first element is the level(top level is 0), the second element is the order in the level")
    edge_percentage: Optional[np.float128] = Field(default=None, ge=0, le=1, description="the percentage of the edge, when it doesn't have its parent entity, it is None")
    parent_entity_name: Optional[str] = Field(default=None, description="the name of the parent entity, when it doesn't have its parent entity, it is None")
    owner_names: Optional[List[str]] = Field(default=None, description="the names of the owners, when it doesn't have its owner, it is None")
    owned_names: Optional[List[str]] = Field(default=None, description="the names of the owned entities, when it doesn't have its owned entity, it is None")

class ApiResponse(BaseModel):
    """API 응답 기본 모델"""
    success: bool = Field(default=True, description="성공 여부")
    message: str = Field(default="계산이 성공적으로 완료되었습니다", description="응답 메시지")
    data: Optional[dict] = Field(None, description="응답 데이터")

class EntitiesIndexMappingDTO(BaseModel):
    """Entities DTO"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    entity_number: int = Field(..., description="the number of the entity")

class DirectIndirectOwnershipRatioDTO(BaseModel):
    """Direct and Indirect Ownership Ratio DTO, the list of the direct and indirect ownership ratio items"""
    direct_indirect_ownership_ratio_items: List[DirectIndirectOwnershipRatioItem] = Field(..., description="the list of the direct and indirect ownership ratio items")

class DirectIndirectOwnershipRatioItem(BaseModel):
    """Direct and Indirect Ownership Ratio Item"""
    owner_entity_name: str = Field(..., description="the name of the owner entity")
    owned_entity_name: str = Field(..., description="the name of the owned entity")
    direct_ownership_ratio: Optional[np.float128] = Field(default=None, description="the direct ownership ratio, when it is not owned by the owner entity, it is None") # 직간접 지분이 있는 상태에서 직접지분은 존재하지 않을 수 있음
    direct_indirect_ownership_ratio: np.float128 = Field(..., description="the direct and indirect ownership ratio, when it is not owned by the owner entity, it is 0") # 직간접 지분이 존재하는 관계만 반환

    @property
    def indirect_ownership_ratio(self) -> np.float128:
        return self.direct_indirect_ownership_ratio - self.direct_ownership_ratio