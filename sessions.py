sessions = {}

def set_human_attending(phone):
    sessions[phone] = "human"

def is_human_attending(phone):
    return sessions.get(phone) == "human" 