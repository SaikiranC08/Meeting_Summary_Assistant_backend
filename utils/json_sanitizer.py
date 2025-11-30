# nlp-service/utils/json_sanitizer.py

def sanitize_summary(json_data: dict):
    """
    Ensures all expected fields exist even if Gemini misses them.
    Prevents frontend crashes and keeps UI consistent.
    """

    safe = {}

    safe["tldr"] = json_data.get("tldr", "")
    safe["executive_summary"] = json_data.get("executive_summary", "")
    safe["progress_updates"] = json_data.get("progress_updates", []) or []
    safe["challenges"] = json_data.get("challenges", []) or []
    safe["risks_blockers"] = json_data.get("risks_blockers", []) or []
    safe["decisions"] = json_data.get("decisions", []) or []
    safe["next_steps"] = json_data.get("next_steps", []) or []
    safe["project_health"] = json_data.get("project_health", "")

    # nested dict
    team = json_data.get("team_alignment", {})
    safe["team_alignment"] = {
        "agreements": team.get("agreements", []) or [],
        "misalignments": team.get("misalignments", []) or [],
        "confusions": team.get("confusions", []) or [],
    }

    return safe
