"""
Configuration Loader Utility

역할:
- YAML 설정 파일을 로드하고 파싱
- 설정값 검증 및 기본값 제공
- 환경별 설정 관리 지원

사용 예시:
    from app.utils.config_loader import load_ai_service_config

    config = load_ai_service_config()
    model_id = config['models']['available'][config['models']['current']]['id']
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    YAML 파일 로드 및 파싱

    Args:
        config_path (str): YAML 파일 경로

    Returns:
        Dict[str, Any]: 파싱된 설정 딕셔너리

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        yaml.YAMLError: YAML 파싱 오류
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logger.info(f"설정 파일 로드 성공: {config_path}")
            return config
        
    except FileNotFoundError:
        logger.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
        raise
    
    except yaml.YAMLError as e:
        logger.error(f"YAML 파싱 오류: {e}")
        raise


def load_ai_service_config() -> Dict[str, Any]:
    """
    AI 서비스 설정 로드

    Returns:
        Dict[str, Any]: AI 서비스 설정 딕셔너리

    Note:
        - config/ai_service.yaml 파일을 로드
        - 프로젝트 루트 디렉토리 기준 상대 경로
    """
    # 프로젝트 루트 디렉토리 찾기
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # app/utils -> app -> project_root

    config_path = project_root / "config" / "ai_service.yaml"

    return load_yaml_config(str(config_path))


def get_current_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    현재 사용 중인 모델 설정 가져오기

    Args:
        config (Dict[str, Any]): AI 서비스 전체 설정

    Returns:
        Dict[str, Any]: 현재 모델의 상세 설정

    Example:
        >>> config = load_ai_service_config()
        >>> model_config = get_current_model_config(config)
        >>> print(model_config['id'])
        'meta-llama/llama-3.2-3b-instruct:free'
    """
    current_model_name = config['models']['current']
    available_models = config['models']['available']

    if current_model_name not in available_models:
        logger.warning(f"현재 모델 '{current_model_name}'이 설정에 없습니다. 기본 모델을 사용합니다.")
        # 첫 번째 사용 가능한 모델 사용
        current_model_name = list(available_models.keys())[0]

    model_config = available_models[current_model_name].copy()
    model_config['name'] = current_model_name

    return model_config


def get_api_parameters(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    API 파라미터 가져오기

    Args:
        config (Dict[str, Any]): AI 서비스 전체 설정

    Returns:
        Dict[str, Any]: API 파라미터 (temperature, max_tokens, top_p)
    """
    return config.get('api_parameters', {
        'temperature': 0.7,
        'max_tokens': 150,
        'top_p': 0.9
    })


def get_prompt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    프롬프트 설정 가져오기

    Args:
        config (Dict[str, Any]): AI 서비스 전체 설정

    Returns:
        Dict[str, Any]: 프롬프트 설정
    """
    return config.get('prompt', {
        'system_message': '당신은 요약 전문가입니다.',
        'user_message_template': '다음 게시글을 요약해주세요.\n\n{title}\n{content}',
        'content_preview_length': 300
    })


# 설정 캐싱 (성능 최적화)
_cached_config: Optional[Dict[str, Any]] = None


def get_cached_ai_service_config() -> Dict[str, Any]:
    """
    캐시된 AI 서비스 설정 반환 (성능 최적화)

    Returns:
        Dict[str, Any]: AI 서비스 설정 딕셔너리

    Note:
        - 첫 호출 시 파일을 로드하고 캐시에 저장
        - 이후 호출은 캐시된 설정 반환
        - 서버 재시작 시 캐시 초기화
    """
    global _cached_config

    if _cached_config is None:
        _cached_config = load_ai_service_config()
        logger.info("AI 서비스 설정을 캐시에 저장했습니다.")

    return _cached_config


def reload_config():
    """
    설정 캐시 강제 리로드

    Note:
        - 런타임 중 설정 파일 변경 시 사용
        - 프로덕션 환경에서는 서버 재시작 권장
    """
    global _cached_config
    _cached_config = None
    logger.info("AI 서비스 설정 캐시를 초기화했습니다.")
    return get_cached_ai_service_config()
