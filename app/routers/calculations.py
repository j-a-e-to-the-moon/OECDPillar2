from fastapi import APIRouter, HTTPException
from typing import List
import numpy as np
from app.basic_structure_model import (ApiResponse,
    CompanyResponse, OwnershipRequest, EntityRequest,
    IncomeInclusionRuleResponse, UnderTaxedPaymentsRuleResponse,
    OrgChartResponse,
    SafeharboursGroup, EffectiveTaxRateCalculationGroup,
    EntitiesIndexMappingDTO,
    DirectIndirectOwnershipRatioDTO
)

router = APIRouter()

def calculate_direct_indirect_ownership_ratio(entity_request: EntitiesIndexMappingDTO, ownership_request: OwnershipRequest) -> DirectIndirectOwnershipRatioDTO:
    """Calculate the direct and indirect ownership ratio"""
    
    # 엔티티 이름을 번호로 매핑하는 딕셔너리 생성
    entity_name_to_number = {entity.entity_name: entity.entity_number for entity in entity_request}
    
    # 최대 엔티티 번호를 찾아서 행렬 크기 결정
    max_entity_number = max(entity.entity_number for entity in entity_request)
    matrix_size = max_entity_number + 1
    
    # direct_ownership_matrix 초기화 (0으로 채워진 정사각 행렬)
    direct_ownership_matrix = np.zeros((matrix_size, matrix_size), dtype=np.float128)
    
    # OwnershipRequest 안의 모든 소유권 관계에 대해 반복해야 함
    for ownership_relation in ownership_request.ownership_relations:  # 예시
        owner_number = entity_name_to_number[ownership_relation.owner_entity_name]
        owned_number = entity_name_to_number[ownership_relation.owned_entity_name]
        percentage = ownership_relation.ownership_percentage
        
        direct_ownership_matrix[owner_number][owned_number] = percentage
    
    result_matrix = direct_ownership_matrix.copy()
    while(not np.equal(direct_ownership_matrix, result_matrix).all()):
        result_matrix = direct_ownership_matrix.copy()
        np.fill_diagonal(result_matrix, 1)
        result_matrix = np.matmul(result_matrix, direct_ownership_matrix)
    
    result = []
    for owner_name, owner_number in entity_name_to_number.items():
        for owned_name, owned_number in entity_name_to_number.items():
            if result_matrix[owner_number][owned_number] > 0:
                result.append(DirectIndirectOwnershipRatioDTO(
                    owner_entity_name=owner_name,
                    owned_entity_name=owned_name,
                    direct_ownership_ratio=direct_ownership_matrix[owner_number][owned_number],
                    direct_indirect_ownership_ratio=result_matrix[owner_number][owned_number]
                ))

    return result

@router.get("/countries/info")
async def get_countries_info():
    """OECD Pillar 2 참여 국가 정보"""
    return {
        "pillar_two_countries": [
            "한국", "미국", "일본", "독일", "프랑스", "영국", "캐나다", "호주",
            "이탈리아", "스페인", "네덜란드", "벨기에", "스위스", "오스트리아",
            "스웨덴", "노르웨이", "덴마크", "핀란드", "아일랜드", "룩셈부르크"
        ],
        "implementation_date": "2024-01-01",
        "description": "OECD Pillar 2는 다국적 기업의 최소세율을 15%로 보장하는 국제 조세 규칙입니다"
    } 

@router.post("/pillar-two-calculation-structure", response_model=DirectIndirectOwnershipRatioDTO)
async def calculate_pillar_two_calculation_structure(request: EntityRequest, ownership_request: OwnershipRequest):
    """
    Pillar 2 계산 구조 계산
    
    모든 법인에 대한 Pillar 2 계산 구조를 계산합니다.
    """
    try:
        direct_indirect_ownership_ratio_list = calculate_direct_indirect_ownership_ratio(request, ownership_request)
        return DirectIndirectOwnershipRatioDTO(direct_indirect_ownership_ratio_items=direct_indirect_ownership_ratio_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"계산 중 오류가 발생했습니다: {str(e)}")