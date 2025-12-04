
class SkillIssue(Exception):
    pass
def setup(userInput):
    raise SkillIssue(f"{userInput} has a skill issue")