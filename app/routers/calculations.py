from fastapi import APIRouter, HTTPException
from typing import List
import numpy as np
from app.basic_structure_model import (ApiResponse,
    CompanyResponse, OwnershipRequest, OwnershipsRequest, EntityRequest, EntitiesRequest,
    IncomeInclusionRuleResponse, UnderTaxedPaymentsRuleResponse,
    OrgChartResponse,
    SafeharboursGroup, EffectiveTaxRateCalculationGroup,
    EntitiesIndexMappingDTO, EntitiesIndexMappingItem,
    EntitySimpleRequest, EntitiesSimpleRequest,
    DirectIndirectOwnershipRatioResponse,
    DirectIndirectOwnershipRatioResponseItem,
    UltimateParentEntityAccountingType,
    CompaniesResponse,
    StructuresResponse,
    IncomeInclusionRulesResponse,
    UnderTaxedPaymentsRulesResponse,
    OrgChartsResponse,
    OwnershipsRequestDTO,
    OwnershipRequestItem
)

router = APIRouter()

def create_entities_simple_index_mapping_dto(ownerships_request: OwnershipsRequest) -> EntitiesIndexMappingDTO:
    """Create the entities index mapping dto for simple entities"""
    # OwnershipsRequest에서 owner, owned 엔티티들을 unique하게 추출
    unique_entities = set()
    
    # ownerships_request에서 owner와 owned 엔티티 이름들을 추출
    for ownership in ownerships_request.ownerships:
        unique_entities.add(ownership.owner_entity_name)
        unique_entities.add(ownership.owned_entity_name)
    
    # unique 엔티티들을 리스트로 변환하고 정렬
    entities_list = sorted(list(unique_entities))
    
    # index mapping 생성
    entities_index_mapping_items = []
    for index, entity_name in enumerate(entities_list):
        entities_index_mapping_items.append(
            EntitiesIndexMappingItem(entity_name=entity_name, entity_number=index)
        )
    
    return EntitiesIndexMappingDTO(entities_index_mapping_items=entities_index_mapping_items)

def create_entities_index_mapping_dto(entities_request: EntitiesRequest) -> EntitiesIndexMappingDTO:
    """Create the entities index mapping dto with priority-based numbering"""
    
    # 엔티티를 타입별로 분류
    ultimate_parent_entities = []
    consolidated_entities = []
    equity_method_entities = []
    etc_entities = []
    
    for entity in entities_request.entities:
        accounting_type = entity.ultimate_parent_entity_accounting_type
        if accounting_type == UltimateParentEntityAccountingType.ULTIMATE_PARENT_ENTITY:
            ultimate_parent_entities.append(entity)
        elif accounting_type == UltimateParentEntityAccountingType.CONSOLIDATED:
            consolidated_entities.append(entity)
        elif accounting_type == UltimateParentEntityAccountingType.EQUITY_METHOD:
            equity_method_entities.append(entity)
        else:  # ETC
            etc_entities.append(entity)
    
    # 우선순위에 따라 번호 부여
    entities_index_mapping_items = []
    current_number = 0
    
    # 1. Ultimate Parent Entity: 0번
    for entity in ultimate_parent_entities:
        entities_index_mapping_items.append(
            EntitiesIndexMappingItem(entity_name=entity.name, entity_number=current_number)
        )
        current_number += 1
    
    # 2. Consolidation: 1번부터
    for entity in consolidated_entities:
        entities_index_mapping_items.append(
            EntitiesIndexMappingItem(entity_name=entity.name, entity_number=current_number)
        )
        current_number += 1
    
    # 3. Equity Method: Consolidation 다음부터
    for entity in equity_method_entities:
        entities_index_mapping_items.append(
            EntitiesIndexMappingItem(entity_name=entity.name, entity_number=current_number)
        )
        current_number += 1
    
    # 4. ETC: 그 다음부터
    for entity in etc_entities:
        entities_index_mapping_items.append(
            EntitiesIndexMappingItem(entity_name=entity.name, entity_number=current_number)
        )
        current_number += 1
    
    return EntitiesIndexMappingDTO(entities_index_mapping_items=entities_index_mapping_items)

def convert_ownerships_to_dto(entities_index_mapping_dto: EntitiesIndexMappingDTO, ownerships_request: OwnershipsRequest) -> OwnershipsRequestDTO:
    """Convert OwnershipsRequest to OwnershipsRequestDTO using entity index mapping"""
    
    # 엔티티 이름을 번호로 매핑하는 딕셔너리 생성
    entity_name_to_number = {entity.entity_name: entity.entity_number for entity in entities_index_mapping_dto.entities_index_mapping_items}
    
    # ownerships를 변환
    ownership_items = []
    for ownership in ownerships_request.ownerships:
        owner_entity_index = entity_name_to_number[ownership.owner_entity_name]
        owned_entity_index = entity_name_to_number[ownership.owned_entity_name]
        
        ownership_items.append(OwnershipRequestItem(
            owner_entity_index=owner_entity_index,
            owned_entity_index=owned_entity_index,
            ownership_percentage=ownership.ownership_percentage
        ))
    
    return OwnershipsRequestDTO(ownerships=ownership_items)

def calculate_direct_indirect_ownership_ratio_core(entities_index_mapping_dto: EntitiesIndexMappingDTO, ownerships_request: OwnershipsRequestDTO) -> DirectIndirectOwnershipRatioResponse:
    """Calculate the direct and indirect ownership ratio"""

    epsilon_for_calculation = 1e-7  # float 정밀도를 고려한 안전한 임계값
    epsilon_for_filtering = 1e-6  # 결과 필터링을 위한 임계값
    decimal_places = 6  # 소수점 자릿수
    
    # 엔티티 인덱스를 이름으로 매핑하는 딕셔너리 생성 (결과에서 이름 표시를 위해)
    entity_index_to_name = {entity.entity_number: entity.entity_name for entity in entities_index_mapping_dto.entities_index_mapping_items}
    
    # ownerships_request에서 unique한 기업 인덱스들 추출
    entity_indices = set()
    for ownership in ownerships_request.ownerships:
        entity_indices.add(ownership.owner_entity_index)
        entity_indices.add(ownership.owned_entity_index)
    
    # 최대 엔티티 번호를 찾아서 행렬 크기 결정
    max_entity_index = max(entity_indices) if entity_indices else 0
    matrix_size = max_entity_index + 1

    # direct_ownership_matrix 초기화 (0으로 채워진 정사각 행렬)
    direct_ownership_matrix = np.zeros((matrix_size, matrix_size), dtype=float)
    
    # ownerships_request의 모든 소유권 관계를 행렬에 채우기
    for ownership in ownerships_request.ownerships:
        owner_index = ownership.owner_entity_index
        owned_index = ownership.owned_entity_index
        percentage = ownership.ownership_percentage
        
        # owner는 행 인덱스, owned는 열 인덱스, percentage는 행렬 성분값
        direct_ownership_matrix[owner_index][owned_index] = percentage
    
    result_matrix = direct_ownership_matrix.copy()
    max_iterations = 1000
    iterations = 0
    while(True):
        # 이전 단계 결과를 저장
        previous_matrix = result_matrix.copy()
        
        np.fill_diagonal(result_matrix, 1)
        result_matrix = np.matmul(result_matrix, direct_ownership_matrix)
        iterations += 1
        
        # 이전 단계와 현재 단계 결과를 비교하여 수렴성 판단
        if iterations >= max_iterations or np.allclose(previous_matrix, result_matrix, atol=epsilon_for_calculation):
            break
    result = []
    for owner_index in entity_indices:
        for owned_index in entity_indices:
            direct_indirect_ratio = result_matrix[owner_index][owned_index]
            
            # epsilon 기준으로 필터링 (작은 값 제외)
            if direct_indirect_ratio > epsilon_for_filtering:
                # 직간접지분 반올림
                direct_indirect_ratio_processed = round(direct_indirect_ratio, decimal_places)
                
                # 인덱스를 이름으로 변환
                owner_name = entity_index_to_name[owner_index]
                owned_name = entity_index_to_name[owned_index]
                
                result.append(DirectIndirectOwnershipRatioResponseItem(
                    owner_entity_name=owner_name,
                    owned_entity_name=owned_name,
                    direct_indirect_ownership_ratio=direct_indirect_ratio_processed
                ))

    return DirectIndirectOwnershipRatioResponse(direct_indirect_ownership_ratio_items=result, iterations=iterations)

@router.post("/pillar-two-calculation-structure", response_model=ApiResponse)
async def calculate_pillar_two_calculation_structure(entities_request: EntitiesRequest, ownerships_request: OwnershipsRequest):
    """
    Pillar 2 계산 구조 계산
    
    모든 법인에 대한 Pillar 2 계산 구조를 계산합니다.
    """
    try:
        entities_index_mapping_dto = create_entities_index_mapping_dto(entities_request)

        ownerships_request_dto = convert_ownerships_to_dto(entities_index_mapping_dto, ownerships_request)
        direct_indirect_ownership_ratio_dto = calculate_direct_indirect_ownership_ratio_core(entities_index_mapping_dto, ownerships_request_dto)
        return ApiResponse(data=StructuresResponse(companies=CompaniesResponse(companies=[]), income_inclusion_rules=IncomeInclusionRulesResponse(income_inclusion_rules=[]), under_taxed_payments_rules=UnderTaxedPaymentsRulesResponse(under_taxed_payments_rules=[]), org_charts=OrgChartsResponse(org_charts=[])))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"계산 중 오류가 발생했습니다: {str(e)}")

@router.post("/pillar-two-calculation-structure/direct-indirect-ownership-ratio", response_model=ApiResponse)
async def calculate_direct_indirect_ownership_ratio(ownerships_request: OwnershipsRequest):
    """
    모든 법인에 대한 직간접 지분 비율을 계산합니다.
    """
    try:
        entities_index_mapping_dto = create_entities_simple_index_mapping_dto(ownerships_request)
        ownerships_request_dto = convert_ownerships_to_dto(entities_index_mapping_dto, ownerships_request)
        direct_indirect_ownership_ratio_dto = calculate_direct_indirect_ownership_ratio_core(entities_index_mapping_dto, ownerships_request_dto)
        return ApiResponse(data=direct_indirect_ownership_ratio_dto, iterations=direct_indirect_ownership_ratio_dto.iterations, success=True, message="직간접 지분 비율 계산이 성공적으로 완료되었습니다")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"계산 중 오류가 발생했습니다: {str(e)}")