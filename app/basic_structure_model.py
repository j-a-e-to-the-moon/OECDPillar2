from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
from enum import Enum
from decimal import Decimal


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

class EntitiesRequest(BaseModel):
    """Multiple Entities Information Request"""
    entities: List[EntityRequest] = Field(..., description="the list of entities")

class OwnershipRequest(BaseModel):
    """Ownership Information Request"""
    owner_entity_name: str = Field(..., description="the name of the owner entity")
    owned_entity_name: str = Field(..., description="the name of the owned entity")
    ownership_percentage: float = Field(..., ge=0, le=1, description="the ownership percentage")

class OwnershipsRequest(BaseModel):
    """Ownerships Information Request"""
    ownerships: List[OwnershipRequest] = Field(..., description="the list of ownerships")

class OwnershipRequestItem(BaseModel):
    """Ownership Information Request Item"""
    owner_entity_index: int = Field(..., description="the index of the owner entity")
    owned_entity_index: int = Field(..., description="the index of the owned entity")
    ownership_percentage: float = Field(..., ge=0, le=1, description="the ownership percentage")

class OwnershipsRequestDTO(BaseModel):
    """Ownerships Information Request DTO"""
    ownerships: List[OwnershipRequestItem] = Field(..., description="the list of ownerships")

class CompanyResponse(BaseModel):
    """Pillar2 Calculation Structure Response for Company"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    parent_entity_type: Optional[ParentEntityType] = Field(None, description="the type of the parent entity, when it is not a parent entity, it is None")
    safeharbours_group: Optional[str] = Field(None, description="the name of the safeharbours group, when it is excluded entity in calculating safe harbours, it is None")
    effective_tax_rate_calculation_group: Optional[str] = Field(None, description="the name of the effective tax rate calculation group, when it is excluded entity in calculating effective tax rate, it is None")
    income_inclusion_rule_taxed_ratio: float = Field(default=0, ge=0, le=1, description="the taxed ratio of the income inclusion rule, when it is not taxed by IIR, it is 0")
    utpr_taxed_ratio: float = Field(default=0, ge=0, le=1, description="the taxed ratio of the undertaxed payments rule, when it is not taxed by UTPR, it is 0")

class CompaniesResponse(BaseModel):
    """Multiple Companies Information Response"""
    companies: List[CompanyResponse] = Field(..., description="the list of companies")

class IncomeInclusionRuleResponse(BaseModel):
    """Income Inclusion Rule Response"""
    parent_entity_name: str = Field(..., description="the name of the parent entity, primary key")
    owned_entity_names: List[str] = Field(..., description="the names of the owned entities")
    direct_indirect_ownership_ratio: float = Field(default=0, ge=0, le=1, description="the ratio of the direct and indirect ownership, when it is not owned by the parent entity, it is 0")
    income_inclusion_ratio: float = Field(default=0, ge=0, le=1, description="the ratio of the income inclusion, when it is not included by IIR, it is 0")
    
    @property
    def offset_ratio(self) -> float:
        return self.direct_indirect_ownership_ratio - self.income_inclusion_ratio
    
class IncomeInclusionRulesResponse(BaseModel):
    """Multiple Income Inclusion Rules Information Response"""
    income_inclusion_rules: List[IncomeInclusionRuleResponse] = Field(..., description="the list of income inclusion rules")

class UnderTaxedPaymentsRuleResponse(BaseModel):
    """Under Taxed Payments Rule Response"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    utpr_taxed_ratio: float = Field(default=0, ge=0, le=1, description="the ratio of the undertaxed payments rule, when it is not taxed by UTPR, it is 0")

class UnderTaxedPaymentsRulesResponse(BaseModel):
    """Multiple Under Taxed Payments Rules Information Response"""
    under_taxed_payments_rules: List[UnderTaxedPaymentsRuleResponse] = Field(..., description="the list of under taxed payments rules")

class OrgChartResponse(BaseModel):
    """Org Chart Response"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    node_location: Tuple[int,int] = Field(..., description="the location of the node in the org chart, the first element is the level(top level is 0), the second element is the order in the level")
    edge_percentage: Optional[float] = Field(default=None, ge=0, le=1, description="the percentage of the edge, when it doesn't have its parent entity, it is None")
    parent_entity_name: Optional[str] = Field(default=None, description="the name of the parent entity, when it doesn't have its parent entity, it is None")
    owner_names: Optional[List[str]] = Field(default=None, description="the names of the owners, when it doesn't have its owner, it is None")
    owned_names: Optional[List[str]] = Field(default=None, description="the names of the owned entities, when it doesn't have its owned entity, it is None")

class OrgChartsResponse(BaseModel):
    """Multiple Org Charts Information Response"""
    org_charts: List[OrgChartResponse] = Field(..., description="the list of org charts")

class StructuresResponse(BaseModel):
    """Structure of Pillar 2 Calculation"""
    companies: CompaniesResponse = Field(..., description="the companies")
    income_inclusion_rules: IncomeInclusionRulesResponse = Field(..., description="the income inclusion rules")
    under_taxed_payments_rules: UnderTaxedPaymentsRulesResponse = Field(..., description="the under taxed payments rules")
    org_charts: OrgChartsResponse = Field(..., description="the org charts")

class ApiResponse(BaseModel):
    """API 응답 기본 모델"""
    success: bool = Field(default=True, description="성공 여부")
    message: str = Field(default="계산이 성공적으로 완료되었습니다", description="응답 메시지")
    data: object = Field(None, description="응답 데이터")

class EntitiesIndexMappingItem(BaseModel):
    """Entities DTO"""
    entity_name: str = Field(..., description="the name of the entity, primary key")
    entity_number: int = Field(..., description="the number of the entity")

class EntitiesIndexMappingDTO(BaseModel):
    """Entities Index Mapping DTO"""
    entities_index_mapping_items: List[EntitiesIndexMappingItem] = Field(..., description="the list of the entities index mapping items")

class EntitySimpleRequest(BaseModel):
    """Entity Simple Request"""
    name: str = Field(..., description="the name of the entity, primary key")

class EntitiesSimpleRequest(BaseModel):
    """Entities Simple Request"""
    entities: List[EntitySimpleRequest] = Field(..., description="the list of the entities")

class DirectIndirectOwnershipRatioResponseItem(BaseModel):
    """Direct and Indirect Ownership Ratio Item"""
    owner_entity_name: str = Field(..., description="the name of the owner entity")
    owned_entity_name: str = Field(..., description="the name of the owned entity")
    direct_indirect_ownership_ratio: float = Field(..., description="the direct and indirect ownership ratio, when it is not owned by the owner entity, it is 0") # 직간접 지분이 존재하는 관계만 반환

class DirectIndirectOwnershipRatioResponse(BaseModel):
    """Direct and Indirect Ownership Ratio DTO, the list of the direct and indirect ownership ratio items"""
    direct_indirect_ownership_ratio_items: List[DirectIndirectOwnershipRatioResponseItem] = Field(..., description="the list of the direct and indirect ownership ratio items")
    iterations: int = Field(..., description="the number of iterations")