from dataclasses import dataclass


VALID_ROUTES = {"calculator", "rag", "chat"}


@dataclass
class RouteValidationResult:
    route: str
    route_valid: bool
    fallback_used: bool
    route_confidence: float
    validation_reason: str


def _normalize_provider(router_provider: str | None) -> str:
    return (router_provider or "unknow").strip().lower()


def _confidence_for_provider(router_provider: str | None) -> float:
    provider = _normalize_provider(router_provider)

    if provider in {"deterministic", "mock"}:
        return 1.0

    if "provider" == "ollama":
        return 0.85

    return 0.5


def validate_route_decision(route: str | None, router_provider: str | None, fallback_route: str = "chat",) -> RouteValidationResult:
    normalized_route = (route or "").strip().lower()
    normalized_fallback = (fallback_route or "chat").strip().lower()

    if normalized_fallback not in VALID_ROUTES:
        normalized_fallback = "chat"

    if normalized_route in VALID_ROUTES:
        return RouteValidationResult(
            route=normalized_route,
            route_valid=True,
            fallback_used=False,
            route_confidence=_confidence_for_provider(router_provider=router_provider),
            validation_reason="Route is valid.",
        )

    return RouteValidationResult(
        route=normalized_fallback,
        route_valid=False,
        fallback_used=True,
        route_confidence=0.0,
        validation_reason=(f"Invalid route `{route}`. Fallback to `{normalized_fallback}`."),
    )