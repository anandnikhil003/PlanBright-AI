from pydantic import BaseModel, Field
from fastapi import File, UploadFile, Form
from typing import Optional, List
from datetime import datetime


class GenerateLessonPlan(BaseModel):
    grade_level: str = Field(description="selected grade level for the students")
    topic: str = Field(
        description="Topic, standard or longer description of what you are teaching"
    )
    additional_criteria: str = Field(
        description="Additional criteria to meet for the lesson plan"
    )
    standards: str = Field(description="Standard to align to for the lesson plan")

    @property
    def user_query(self) -> str:
        if len(self.standards) == 0:
            standards = "None"
        else:
            standards = self.standards
        if len(self.additional_criteria) == 0:
            criteria = "None"
        else:
            criteria = self.additional_criteria
        query = f""" Help me write a lesson plan for 
        Grade: {self.grade_level} 
        Topic: {self.topic} 
        Additional Critieria: {criteria} 
        Standards to align to: {standards} """
        return query


class ExpandLessonPlan(BaseModel):
    id: str = Field(description="lesson plan id")
    query: str = Field(description="query to expand lesson plan with")


class LessonPlanResponse(BaseModel):
    id: str = Field(description="lesson plan id")
    response: str = Field(description="response from lesson planner")


class ExpandLessonPlanResponse(BaseModel):
    id: str = Field(description="lesson plan id")
    expanded_response: str = Field(description="response from lesson planner")


class GenerateAssessment(BaseModel):
    learning_objectives: str
    assesment_type: str
    grade: str
    skills: str
    subject: str

    @property
    def user_query(self) -> str:
        query = f""" Help me generate an assesment for 
        Subject: {self.subject}
        Grade: {self.grade} 
        Topic: {self.skills}
        Standards: {self.learning_objectives} 
        Preferred Assessment Type: {self.assesment_type} """
        return query


class GenerateAssessmentEdit(GenerateAssessment):
    assesment_type_two: str


class AssesmentResponse(BaseModel):
    id: str = Field(description="assesment id")
    response: str = Field(description="response from assesment generator")


class GenerateRubrik(BaseModel):
    project_description: str = Field(
        description="assignment or project requiring a rubric"
    )
    evaluation_criteria: str = Field(
        description="evauluation criteria described by the user"
    )
    level_of_achievement: str = Field(description="describe performance levels")
    standards_alignment: str = Field(
        description="standards that the rubric aligns with"
    )
    flexibility_needs: str = Field(
        description=" if rubric needs to accommodate diverse learning paths"
    )

    @property
    def user_query(self) -> str:
        query = f""" Help me write a rubrik for 
        Project Description: {self.project_description} 
        Evaluation Criteria: {self.evaluation_criteria} 
        Level of Achievement: {self.level_of_achievement} 
        Standards Alignment: {self.standards_alignment} 
        Flexibility Needs: {self.flexibility_needs} """
        return query


class GenerateDiffrentiation(BaseModel):
    grade: str
    desired_outcomes: str
    lesson_plan: str
    diffrentiation_types: str
    learning_profiles: str

    @property
    def user_query(self) -> str:
        query = f""" Help me write a diffrentiation for 
        Grade: {self.grade} 
        Subject/Topic: {self.lesson_plan}
        Standards: {self.desired_outcomes}
        Proficiency of students: {self.learning_profiles} 
        Differentiation Type: {self.diffrentiation_types} 
        Assessment type: {self.diffrentiation_types}"""
        return query


class DiffrentiationResponse(BaseModel):
    id: str
    diffrentiation: str


class InteractionResponseAiCoach(BaseModel):
    user_id: str = Field(description="id of the user")
    bot_interaction: int = Field(description="Number of interactions with the bot")


class InteractionResponseLessonPlan(BaseModel):
    user_id: str = Field(description="id of the user")
    lesson_plan_interaction: int = Field(
        description="Number of interactions with the lesson planner"
    )


class InteractionResponseRubrik(BaseModel):
    user_id: str = Field(description="id of the user")
    rubrik_interaction: int = Field(
        description="Number of interactions with the Rubrik Generator"
    )


class InteractionResponseAssesment(BaseModel):
    user_id: str = Field(description="id of the user")
    assesment_interaction: int = Field(
        description="Number of interactions with the Assessment Generator"
    )


class InteractionResponseDiffrentiation(BaseModel):
    user_id: str = Field(description="id of the user")
    diffrentiation_interaction: int = Field(
        description="Number of interactions with the Diffrentiation Generator"
    )


class InteractionResponseIep(BaseModel):
    user_id: str = Field(description="id of the user")
    IEP_interaction: int = Field(
        description="Number of interactions with the IEP Generator"
    )


class InteractionResponseUnitPlanner(BaseModel):
    user_id: str = Field(description="id of the user")
    Unitplan_interaction: int = Field(
        description="Number of interactions with the Unit Planner"
    )


class InteractionResponseFeedback(BaseModel):
    user_id: str = Field(description="id of the user")
    feedback_interaction: int = Field(
        description="Number of interactions with the Feedback Generator"
    )


class TotalInteractionResponse(BaseModel):
    user_id: str = Field(description="id of the user")
    overall_interaction: int = Field(
        description="Number of total interactions with the apps"
    )


class PDFQuery(BaseModel):
    file: UploadFile = File(..., description="Upload a PDF file")
    document_type: str = Form(
        ...,
        description="Enter document type (school or persona)",
        regex="^(school|persona)$",
    )


class CleanedHistoryResponse(BaseModel):
    chat_history_id: str
    user_query: str
    is_favorite: bool


class ChatHistoryListItem(BaseModel):
    message_type: str
    id: str
    created_at: datetime
    user_query: str
    coach_response: str


class AgentMainItem(BaseModel):
    message_type: str
    id: str
    created_at: datetime
    coach_response: str


class FeedbackData(BaseModel):
    feedback: str
    feedback_description: str


class EditQuery(BaseModel):
    edited_query: str


class ChatMessage(BaseModel):
    chat_msg_id: str
    user_query: str
    chat_response: str


class AgentList(BaseModel):
    agent_id: str
    agent_response: str
    chats: Optional[List[ChatMessage]] = []


class IDList(BaseModel):
    agent_id: str
    date: datetime
    user_query_title: str


class ExtractedPdfContent(BaseModel):
    extracted_content: str


class ExtractedDocxContent(BaseModel):
    extracted_content: str


class GenerateIEP(BaseModel):
    grade: str
    date_of_birth: Optional[str] = Field(default=None)
    eligibility: str
    people_providing_services: Optional[str] = Field(default=None)
    parent_feedback: Optional[str] = Field(default=None)
    teacher_feedback: Optional[str] = Field(default=None)
    academic_performance: str
    functional_performance: Optional[str] = Field(default=None)
    strengths: str
    needs: str
    services_provided: Optional[str] = Field(default=None)
    postsecondary_goals: Optional[str] = Field(default=None)

    @property
    def user_query(self) -> str:
        query = f""" Help me generate an iep for 
        Grade: {self.grade}
        Date of Birth: {self.date_of_birth or 'Not Provided'} 
        Eligibility: {self.eligibility}
        People Providing Services: {self.people_providing_services or 'Not Provided'} 
        Parent Feedback: {self.parent_feedback or 'Not Provided'}
        Teacher Feedback: {self.teacher_feedback or 'Not Provided'} 
        Academic Performance: {self.academic_performance}
        Functional Performance: {self.functional_performance or 'Not Provided'}
        Strengths: {self.strengths}
        Needs: {self.needs}
        Services Provided & Service Delivery: {self.services_provided or 'Not Provided'}
        Postsecondary Goals: {self.postsecondary_goals or 'Not Provided'}"""
        return query


# Need to edit this, waiting for PRD table from Unit Planner
class GenerateUnitPlan(BaseModel):
    grade: str
    unit_title: Optional[str] = Field(default=None)
    subject: str
    unit_objectives: Optional[str] = Field(default=None)
    standard: Optional[str] = Field(default=None)
    length_of_a_unit: str
    assessment_strategies: Optional[str] = Field(default=None)
    interdisciplinary_links: Optional[str] = Field(default=None)
    additional_comments: Optional[str] = Field(default=None)

    @property
    def user_query(self) -> str:
        query = f""" Help me generate a unit plan for 
        Grade: {self.grade}
        Unit Title: {self.unit_title or 'Not Provided'} 
        Subject: {self.subject}
        Unit Objectives: {self.unit_objectives or 'Not Provided'} 
        Standard: {self.standard or 'Not Provided'}
        Length of a Unit: {self.length_of_a_unit} 
        Assessment Strategies: {self.assessment_strategies or 'Not Provided'}
        Interdisciplinary Links: {self.interdisciplinary_links or 'Not Provided'}
        Additional Comments: {self.additional_comments or 'Not Provided'}"""
        return query


class FavoriteRequest(BaseModel):
    message_id: str
    user_id: str
    user_query: str
    is_favorite: bool


class TranslationRequest(BaseModel):
    text: str
    target_language: str


class TranslationLanguageRequest(BaseModel):
    target_language: str


class AICoachHistoryResponse(BaseModel):
    chat_history_id: str
    user_id: str
    summary_title: str


class QuickActionResponse(BaseModel):
    response: str
    table_name: str


class GenerateFeedback(BaseModel):
    assignment: str
    feedback_criteria: Optional[str] = Field(default=None)
    achievement_levels: Optional[str] = Field(default=None)
    standards_alignment: Optional[str] = Field(default=None)
    tone_and_style_controls: Optional[str] = Field(default=None)

    @property
    def user_query(self) -> str:
        query = f""" Help me generate an feedback for 
        Assignment/Project: {self.assignment}
        Feedback Criteria: {self.feedback_criteria or 'Not Provided'} 
        Achievement Levels: {self.achievement_levels or 'Not Provided'} 
        Standards Alignment: {self.standards_alignment or 'Not Provided'}
        Tone and Style Controls: {self.tone_and_style_controls or 'Not Provided'} 
        """
        return query


class ShareLinkData(BaseModel):
    url_data: str


class ShareSessionID(BaseModel):
    id: str


class NewTags(BaseModel):
    new_tag: List[str]
