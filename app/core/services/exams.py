import json
from typing import Dict, List
from uuid import UUID

from loguru import logger
from sqlalchemy import String, cast, select
from sqlalchemy.exc import IntegrityError

from app.core.models import LanguageModel
from app.core.models.exams import (
    ExamsModel,
    PapersModel,
    SectionsModel,
    SubSectionQuestionsModel,
    SubSectionsModel,
    TemplatesModel,
)
from app.core.schemas.exams import (
    ExamsCreateDatabaseSchema,
    ExamsUpdateDatabaseSchema,
    PapersCreateDatabaseSchema,
    PapersUpdateDatabaseSchema,
    SectionsCreateDatabaseSchema,
    SectionsUpdateDatabaseSchema,
    SubSectionQuestionsCreateDatabaseSchema,
    SubSectionQuestionsUpdateDatabaseSchema,
    SubSectionsCreateDatabaseSchema,
    SubSectionsUpdateDatabaseSchema,
    TemplatesCreateDatabaseSchema,
    TemplatesUpdateDatabaseSchema,
)
from app.core.services.base import BaseService, SoftDeleteBaseService
from app.core.services.questions import LanguageService, QuestionsService
from app.core.services.utils import helper_functions
from app.enums import PapersStatusEnum
from app.schemas import (
    CBTPaperBaseSchema,
    CBTQuestionsResponseSchema,
    CBTQuestionUpdateSchema,
    CBTRequestSchema,
    CBTResponseSchema,
    CBTSectionsResponseSchema,
    CBTSubSectionsResponseSchema,
)
from app.utils.exceptions.common_exceptions import DataLogicException, UUIDNotFoundException


class ExamsService(SoftDeleteBaseService[ExamsModel, ExamsCreateDatabaseSchema, ExamsUpdateDatabaseSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=ExamsModel, **kwargs)

    # Create Functions

    async def create_bulk(self, exams: List[ExamsCreateDatabaseSchema]) -> List[ExamsModel]:
        """
        An extension of create function to unique names for exams
        :param exams: List of exam data that needs to be added to the table
        :return: List of exam instances that were created
        """
        exam_names = [exam.name for exam in exams]

        exam_instances = await self.filter([self.model.name.in_(exam_names)])
        existing_exam_names = [exam_instance.name for exam_instance in exam_instances]

        if existing_exam_names:
            logger.warning(f"Exams with names {', '.join(existing_exam_names)} already exists")

        # Create the new exams
        new_exams = [exam for exam in exams if exam.name not in existing_exam_names]
        new_exam_instances = await super().create_bulk(new_exams)

        return helper_functions.order_result(exam_instances + new_exam_instances, exam_names, "name")

    # Get Functions

    async def get_exams(self, include_inactive: bool) -> List[ExamsModel]:
        """
        Get all the exams that are available in the database and are in active state
        :return: List of active exam instances
        """
        if include_inactive:
            return await self.get_all()
        return await self.filter([self.model.is_active.is_(True)])

    async def get_papers(self, exam_id: UUID, paper_status: PapersStatusEnum) -> List[PapersModel]:
        """
        Get all the papers for a particular exam. Say for JEE Mains exam, get all the papers (i.e. 2021, 2022, etc.)
        :param exam_id: Exam ID for which papers need to be fetched
        :param paper_status: Status of the paper
        :return: List of papers for the exam
        """
        # Check the existence of the exam
        exam_instance = await self.get(exam_id)
        if not exam_instance:
            error_message = f"Exam with ID {exam_id} not found"
            logger.error(error_message)
            raise UUIDNotFoundException(model=ExamsModel, uuid=exam_id)

        # Get the papers where exam_id = exam_id
        papers_service = PapersService(session=self.session)
        paper_instances = await papers_service.filter(
            [PapersModel.exam_id == exam_id, PapersModel.status == paper_status]
        )
        if paper_instances:
            return paper_instances
        return []

    # Update Functions

    async def update_active_status(self, exam_id: UUID, is_active: bool) -> ExamsModel:
        """
        Update the active status of the exam with the given UUID.
        :param exam_id: UUID for the exam.
        :param is_active: Active status to be updated to
        :return: Exam instance that was updated
        """
        exam_instance = await self.get(exam_id)
        if not exam_instance:
            error_message = f"Exam with ID {exam_id} not found"
            logger.error(error_message)
            raise UUIDNotFoundException(model=ExamsModel, uuid=exam_id)

        # Check if the status is same as of the exam
        if exam_instance.is_active == is_active:
            error_message = f"Exam with ID {exam_id} already has {is_active} status"
            raise DataLogicException(error_message)

        return await self.update(exam_instance, ExamsUpdateDatabaseSchema(is_active=is_active))


class PapersService(SoftDeleteBaseService[PapersModel, PapersCreateDatabaseSchema, PapersUpdateDatabaseSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=PapersModel, **kwargs)

    # CREATE Functions

    async def create_paper(self, exam_id: UUID, paper_data: CBTRequestSchema) -> PapersModel:
        """
        Create a new paper for an exam. Say for JEE Mains exam, create a paper for 2021.
        :param exam_id: Exam ID for which paper needs to be created
        :param paper_data: Paper data that needs to be added to the table
        :return: Paper instance that was created
        """
        # Check the existence of the exam
        exam_instance = await ExamsService(session=self.session).get(exam_id)
        if not exam_instance:
            error_message = f"Exam with ID {exam_id} not found"
            logger.error(error_message)
            raise UUIDNotFoundException(model=ExamsModel, uuid=exam_id)

        # Add template for the paper
        templates_service = TemplatesService(session=self.session)
        template_instance = await templates_service.create(
            TemplatesCreateDatabaseSchema(
                name=paper_data.name,
                settings=paper_data.settings.dict(),
                instructions=paper_data.instructions,
            )
        )

        # Fetch the language from the database
        language = paper_data.language
        language_service = LanguageService(session=self.session)
        language_instance = await language_service.create(language)
        language_uuid = language_instance.uuid

        # Create the paper
        try:
            paper_instance = await self.create(
                PapersCreateDatabaseSchema(
                    **paper_data.dict(), exam_id=exam_id, template_id=template_instance.uuid, language_id=language_uuid
                )
            )
        except IntegrityError:
            error_message = f"Paper already exists for the exam id {exam_id}"
            raise DataLogicException(
                error_message,
                paper_name=paper_data.name,
                year=paper_data.year,
                paper_set=paper_data.paper_set,
                exam_id=exam_id,
            )

        # Create sections for the paper
        sections_service = SectionsService(session=self.session)
        sections_instances = await sections_service.create_bulk(
            [
                SectionsCreateDatabaseSchema(**section.dict(), paper_id=paper_instance.uuid, order=idx)
                for idx, section in enumerate(paper_data.sections)
            ]
        )

        # Create sub-sections for the paper
        sub_sections_service = SubSectionsService(session=self.session)
        for section_instance, paper_section in zip(sections_instances, paper_data.sections):
            # Zip is possible because the order of sections and paper_data.sections is same
            sub_sections = paper_section.sub_sections
            sub_sections_instances = await sub_sections_service.create_bulk(
                [
                    SubSectionsCreateDatabaseSchema(**sub_section.dict(), section_id=section_instance.uuid, order=idx)
                    for idx, sub_section in enumerate(sub_sections)
                ]
            )

            # Create questions for the paper
            sub_section_questions_service = SubSectionQuestionsService(session=self.session)
            for sub_section_instance, sub_section in zip(sub_sections_instances, sub_sections):
                # Upload Questions to Questions table
                questions_service = QuestionsService(session=self.session)

                # Updating the language of questions
                for question in sub_section.questions:
                    if not question.language:
                        question.language = language

                question_instances = await questions_service.create_bulk(
                    [question.dict() for question in sub_section.questions]
                )

                await sub_section_questions_service.create_bulk(
                    [
                        SubSectionQuestionsCreateDatabaseSchema(
                            sub_section_id=sub_section_instance.uuid,
                            question_id=question_instance.uuid,
                            positive_marks=question.positive_marks,
                            negative_marks=question.negative_marks,
                            order=idx,
                        )
                        for idx, (question_instance, question) in enumerate(
                            zip(question_instances, sub_section.questions)
                        )
                    ]
                )

        return paper_instance

    # GET Functions

    async def fetch_paper_data(self, paper_id: UUID):
        """
        This function provides all the data related to a paper, using joins
        Result is List of tuples with the following order:
        PapersModel, TemplatesModel, SectionsModel, SubSectionsModel, SubSectionQuestionsModel, QuestionsModel
        :param paper_id: UUID for the paper
        :return: List of tuples with the data
        """
        stmt = (
            select(
                PapersModel, LanguageModel, TemplatesModel, SectionsModel, SubSectionsModel, SubSectionQuestionsModel
            )  # DO NOT CHANGE THE ORDER UNLESS ABSOLUTELY NECESSARY
            .join(LanguageModel, PapersModel.language_id == LanguageModel.uuid)  # noqa
            .join(TemplatesModel, PapersModel.template_id == TemplatesModel.uuid)
            .join(SectionsModel, PapersModel.uuid == SectionsModel.paper_id)
            .join(SubSectionsModel, SectionsModel.uuid == SubSectionsModel.section_id)
            .join(SubSectionQuestionsModel, SubSectionsModel.uuid == SubSectionQuestionsModel.sub_section_id)
            .where(PapersModel.uuid == paper_id)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def get_for_cbt(self, paper_id: UUID) -> CBTResponseSchema:
        """
        Get the paper with settings, sections, subsections, and questions.
        :param paper_id: UUID for the paper
        :return Paper related data in CBTResponseSchema
        """
        paper_data = await self.fetch_paper_data(paper_id)

        if not paper_data:
            raise UUIDNotFoundException(model=PapersModel, uuid=paper_id)

        # Unpack the list of tuples to get the data
        # paper_instance and template_instance are single instances and hence not assigning as list
        sections_instances = set()
        sub_sections_instances = set()
        sub_section_questions_instances = set()

        # Assigning the data to the respective instances
        paper_instance = paper_data[0][0]
        language_instance = paper_data[0][1]
        template_instance = paper_data[0][2]

        for data in paper_data:
            # Adding it to set as we need unique instances
            sections_instances.add(data[3])
            sub_sections_instances.add(data[4])
            sub_section_questions_instances.add(data[5])

        # Get the questions in QuestionsResponseSchema format
        questions_service = QuestionsService(session=self.session)
        question_instances = await questions_service.get_for_cbt(
            [sub_section_questions.question_id for sub_section_questions in sub_section_questions_instances]
        )

        # Linking questions response with sub_section
        question_cbt_response = {}
        for sub_section_question_instance, question_instance in zip(
            sub_section_questions_instances, question_instances
        ):
            question_cbt_response.setdefault(sub_section_question_instance.sub_section_id, []).append(
                (
                    CBTQuestionsResponseSchema(
                        **question_instance.dict(),
                        positive_marks=sub_section_question_instance.positive_marks,
                        negative_marks=sub_section_question_instance.negative_marks,
                    ),
                    sub_section_question_instance.order,
                )
            )

        for key, value in question_cbt_response.items():
            question_cbt_response[key] = helper_functions.order_response(value)

        sub_section_cbt_response = {}
        for sub_section_instance in sub_sections_instances:
            sub_section_cbt_response.setdefault(sub_section_instance.section_id, []).append(
                (
                    CBTSubSectionsResponseSchema(
                        uuid=sub_section_instance.uuid,
                        name=sub_section_instance.name,
                        questions=question_cbt_response.get(sub_section_instance.uuid, []),
                    ),
                    sub_section_instance.order,
                )
            )

        for key, value in sub_section_cbt_response.items():
            sub_section_cbt_response[key] = helper_functions.order_response(value)

        section_cbt_response = [
            (
                CBTSectionsResponseSchema(
                    uuid=section_instance.uuid,
                    name=section_instance.name,
                    section_time=section_instance.section_time,
                    sub_sections=sub_section_cbt_response.get(section_instance.uuid, []),
                ),
                section_instance.order,
            )
            for section_instance in sections_instances
        ]

        # Order the sections based on the order
        section_cbt_response = helper_functions.order_response(section_cbt_response)

        return CBTResponseSchema(
            uuid=paper_instance.uuid,
            name=paper_instance.name,
            year=paper_instance.year,
            language=language_instance.name,
            paper_set=paper_instance.paper_set,
            settings=template_instance.settings,
            instructions=template_instance.instructions,
            sections=section_cbt_response,
        )

    async def get_solution(self, paper_id: UUID) -> Dict[UUID, List]:
        """
        This function provides solution for all the questions in a paper
        :param paper_id: UUID for the paper
        :return: Dictionary of question_id and list of answer/correct options
        """
        paper_data = await self.fetch_paper_data(paper_id)

        # Unpack the list of tuples to get the questions
        sub_section_questions_instances = {data[5] for data in paper_data}

        # Get the solution of the questions
        questions_service = QuestionsService(session=self.session)
        return await questions_service.get_solution(
            [sub_section_questions.question_id for sub_section_questions in sub_section_questions_instances]
        )

    # UPDATE Functions

    async def update_status(self, paper_id: UUID, status: PapersStatusEnum) -> PapersModel:
        """
        Update the status of the paper with the given UUID.
        :param paper_id: UUID for the paper.
        :param status: Status to be updated to
        :return: Paper instance that was published
        """
        paper_instance = await self.get(paper_id)
        if not paper_instance:
            error_message = f"Paper with ID {paper_id} not found"
            logger.error(error_message)
            UUIDNotFoundException(model=PapersModel, uuid=paper_id)

        # Check if the status is same as of the paper
        if paper_instance.status == status:
            error_message = f"Paper with ID {paper_id} already has {status.value} status"
            raise DataLogicException(error_message)

        # In case the paper is in draft status, update the status to the new status
        # (Since not equal - possible values are PUBLISHED and ARCHIVED)
        elif paper_instance.status == PapersStatusEnum.DRAFT:
            updated_instance = await self.update(paper_instance, dict(status=status))

        # Once the paper is published/archived, it cannot be changed to draft status
        elif status == PapersStatusEnum.DRAFT:
            error_message = (
                f"Paper with ID {paper_id} has {paper_instance.status.value} status "
                f"and cannot be changed to {status.value} status"
            )
            raise DataLogicException(error_message)
        else:
            updated_instance = await self.update(paper_instance, dict(status=status))

        return updated_instance

    async def update_paper(self, paper_id: UUID, paper_data: CBTPaperBaseSchema) -> PapersModel:
        """
        This function will allow to update the paper data. Excluding sections, we can update all the fields
        :param paper_id: UUID for the paper.
        :param paper_data: Paper data that needs to be updated
        :return: Paper instance that was updated
        """
        paper_instance = await self.get(paper_id)
        if not paper_instance:
            error_message = f"Paper with ID {paper_id} not found"
            logger.error(error_message)
            UUIDNotFoundException(model=PapersModel, uuid=paper_id)

        # Update the Templates data
        # Since Templates data is unique, we won't update the existing entry, rather create new one
        templates_service = TemplatesService(session=self.session)
        template_instance = await templates_service.create(
            TemplatesCreateDatabaseSchema(
                name=paper_data.name,
                settings=paper_data.settings.dict(),
                instructions=paper_data.instructions,
            )
        )

        # Update the language data
        # Since Language data is unique, we won't update the existing entry, rather create new one
        language_service = LanguageService(session=self.session)
        language_instance = await language_service.create(paper_data.language)

        # Update the paper data
        updated_instance = await self.update(
            paper_instance,
            PapersUpdateDatabaseSchema(
                **paper_data.dict(),
                template_id=template_instance.uuid,
                language_id=language_instance.uuid,
            ),
        )

        return updated_instance


class TemplatesService(BaseService[TemplatesModel, TemplatesCreateDatabaseSchema, TemplatesUpdateDatabaseSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=TemplatesModel, **kwargs)

    async def create(self, template_data: TemplatesCreateDatabaseSchema) -> TemplatesModel:
        """
        Creates Unique template, and in case it exists, returns the existing template.
        :param template_data: Template data that needs to be added to the table
        :return: Template instance that was created
        """
        # Filter the records based on settings and instructions
        template_instance = await self.filter(
            [
                cast(self.model.settings, String) == json.dumps(template_data.settings),
                self.model.instructions == template_data.instructions,
            ]
        )
        if template_instance:
            logger.info(f"Template already exists, with uuid {template_instance[0].uuid}")
            return template_instance[0]

        return await super().create(template_data)


class SectionsService(BaseService[SectionsModel, SectionsCreateDatabaseSchema, SectionsUpdateDatabaseSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=SectionsModel, **kwargs)

    async def update(self, section_id: UUID, section_data: SectionsUpdateDatabaseSchema):
        """
        This function will allow users to update section data in database
        :param section_id: Section ID that needs to be updated
        :param section_data: Section data that needs to be updated
        :return: Section instance that was updated
        """
        section_instance = await self.get(section_id)
        if not section_instance:
            error_message = f"Section with ID {section_id} not found"
            logger.error(error_message)
            UUIDNotFoundException(model=SectionsModel, uuid=section_id)

        return await super().update(section_instance, section_data.dict(exclude_unset=True))


class SubSectionsService(
    BaseService[SubSectionsModel, SubSectionsCreateDatabaseSchema, SubSectionsUpdateDatabaseSchema]
):
    def __init__(self, **kwargs):
        super().__init__(model=SubSectionsModel, **kwargs)

    async def update(self, sub_section_id: UUID, sub_section_data: SubSectionsUpdateDatabaseSchema):
        """
        This function will allow users to update sub-section data in database
        :param sub_section_id: Sub-section ID that needs to be updated
        :param sub_section_data: Sub-section data that needs to be updated
        :return: Sub-section instance that was updated
        """
        sub_section_instance = await self.get(sub_section_id)
        if not sub_section_instance:
            error_message = f"Sub-section with ID {sub_section_id} not found"
            logger.error(error_message)
            UUIDNotFoundException(model=SubSectionsModel, uuid=sub_section_id)

        return await super().update(sub_section_instance, sub_section_data.dict(exclude_unset=True))

    async def update_question(self, sub_section_id: UUID, question_id: UUID, question_data: CBTQuestionUpdateSchema):
        """
        This function will allow users to update question data in a sub-section.
        :param sub_section_id: Sub-section ID that needs to be updated
        :param question_id: Question ID that needs to be updated
        :param question_data: Question data that needs to be updated
        :return: Sub-section instance that was updated
        """
        sub_section_instance = await self.get(sub_section_id)
        if not sub_section_instance:
            error_message = f"Sub-section with ID {sub_section_id} not found"
            logger.error(error_message)
            UUIDNotFoundException(model=SubSectionsModel, uuid=sub_section_id)

        # Update positive and negative marks for the question
        positive_marks = question_data.positive_marks
        negative_marks = question_data.negative_marks
        if positive_marks or negative_marks:
            sub_section_questions_service = SubSectionQuestionsService(session=self.session)
            sub_section_question_instance = await sub_section_questions_service.filter(
                [
                    SubSectionQuestionsModel.sub_section_id == sub_section_id,
                    SubSectionQuestionsModel.question_id == question_id,
                ]
            )
            if not sub_section_question_instance:
                error_message = f"Question with ID {question_id} is not linked with Sub-section {sub_section_id}"
                logger.error(error_message)
                DataLogicException(error_message)

            # Update the positive and negative marks
            await sub_section_questions_service.update(
                sub_section_question_instance[0],
                SubSectionQuestionsUpdateDatabaseSchema(positive_marks=positive_marks, negative_marks=negative_marks),
            )

        # Update the question data
        question_service = QuestionsService(session=self.session)
        return await question_service.update(question_id, question_data)


class SubSectionQuestionsService(
    BaseService[
        SubSectionQuestionsModel, SubSectionQuestionsCreateDatabaseSchema, SubSectionQuestionsUpdateDatabaseSchema
    ]
):
    def __init__(self, **kwargs):
        super().__init__(model=SubSectionQuestionsModel, **kwargs)
