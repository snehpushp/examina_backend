from typing import Dict, List
from uuid import UUID

from app.core.models.questions import (
    LanguageModel,
    OptionsModel,
    PassagesModel,
    QuestionsModel,
    QuestionTagsModel,
    RangeAnswersModel,
    SubjectsModel,
    TagsModel,
)
from app.core.schemas.questions import (
    LanguageCreateUpdateSchema,
    OptionsCreateSchema,
    OptionsUpdateSchema,
    PassagesCreateUpdateSchema,
    QuestionsCreateSchema,
    QuestionsUpdateSchema,
    QuestionsUploadSchema,
    QuestionTagsCreateUpdateSchema,
    RangeAnswerCreateSchema,
    RangeAnswerUpdateSchema,
    RangeAnswerUploadSchema,
    SubjectsCreateSchema,
    SubjectsUpdateSchema,
    TagsCreateUpdateSchema,
)
from app.core.services.base import BaseService
from app.core.services.utils import helper_functions
from app.enums import ContentTypeEnum, LanguageEnum, QuestionTypeEnum
from app.schemas import CBTOptionsResponseSchema, CBTQuestionUpdateSchema, QuestionsResponseSchema
from app.utils.exceptions.common_exceptions import DataLogicException


class QuestionsService(BaseService[QuestionsModel, QuestionsCreateSchema, QuestionsUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=QuestionsModel, **kwargs)

    # Create Functions

    async def create(self, question_dict: dict) -> QuestionsModel:
        """
        This function allows us to upload a new record in the database.
        - If the subject is not present in the database, it will create a new subject.
        - If the tags are not present in the database, it will create new tags.

        :param question_dict: Data to be uploaded in the database
        :return: Question Model
        """
        # Add language if not present
        if "language" not in question_dict:
            question_dict["language"] = LanguageEnum.ENGLISH

        # Parse the question_data to the schema
        question_upload_obj = QuestionsUploadSchema.parse_obj(question_dict)

        # Fetch the subject_uuid from the database
        subject = question_upload_obj.subject
        subject_service = SubjectsService(session=self.session)
        subject_instance = await subject_service.create(subject)
        subject_uuid = subject_instance.uuid

        # Fetch the language from the database
        language = question_upload_obj.language
        language_service = LanguageService(session=self.session)
        language_instance = await language_service.create(language)
        language_uuid = language_instance.uuid

        question = QuestionsCreateSchema(
            **question_upload_obj.dict(), subject_id=subject_uuid, language_id=language_uuid
        )

        # Add passage to the database
        if question_upload_obj.passage:
            passage_service = PassagesService(session=self.session)
            passage_instance = await passage_service.create(
                PassagesCreateUpdateSchema(passage_text=question_upload_obj.passage)
            )
            question.passage_id = passage_instance.uuid

        # Now we'll check if the tags are present in the database
        tags = question_upload_obj.tags
        if tags:
            tag_service = TagsService(session=self.session)
            tags_instances = await tag_service.create_bulk(
                [TagsCreateUpdateSchema(tag_name=tag, subject_id=subject_uuid) for tag in tags]
            )

            # Add the question to the database
            question_instance = await super().create(question)

            # Add these tags to the question
            question_tags_service = QuestionTagsService(session=self.session)
            await question_tags_service.create_bulk(
                [
                    QuestionTagsCreateUpdateSchema(question_id=question_instance.uuid, tag_id=tag_instance.uuid)
                    for tag_instance in tags_instances
                ]
            )
        else:
            # Add the question to the database
            question_instance = await super().create(question)

        # Add the answers based on the type of question
        question_type = QuestionTypeEnum(question_instance.question_type)

        if question_type == QuestionTypeEnum.MCQ or question_type == QuestionTypeEnum.MSQ:
            options = question_upload_obj.options

            if not options:
                raise DataLogicException(
                    "Question is MCQ/MSQ Type but does not contain any options.",
                    question_uuid=question_instance.uuid,
                    options=options,
                )

            # Add options to the database
            options_service = OptionsService(session=self.session)
            await options_service.create_bulk(
                [OptionsCreateSchema(**option.dict(), question_id=question_instance.uuid) for option in options]
            )

        elif question_type == QuestionTypeEnum.NAT:
            answer = question_upload_obj.answer
            # Check the instance of answer in question_data
            if not isinstance(question_upload_obj.answer, RangeAnswerUploadSchema):
                raise DataLogicException(
                    "Question is Value Problem Type but does not contain start and end.",
                    question_uuid=question_instance.uuid,
                    answer=answer,
                )
            range_answer_service = RangeAnswersService(session=self.session)
            await range_answer_service.create(
                RangeAnswerCreateSchema(question_id=question_instance.uuid, **answer.dict())
            )
        # Else is not required as currently we only have 3 types of questions - MCQ, MSQ, NAT

        return question_instance

    async def create_bulk(self, questions_dict: List[dict]) -> List[QuestionsModel]:
        """
        This function allows us to upload multiple records in the database.
        - If the subject is not present in the database, it will create a new subject.
        - If the tags are not present in the database, it will create new tags.

        :param questions_dict: List of data to be uploaded in the database
        :return: List of Question Models
        """
        # Add default language if not present
        for question in questions_dict:
            if "language" not in question:
                question["language"] = LanguageEnum.ENGLISH

        # Parse the questions_dict to the schema
        questions_upload_obj = [QuestionsUploadSchema.parse_obj(question) for question in questions_dict]

        # Fetch the subject_uuid from the database
        subject_service = SubjectsService(session=self.session)
        subjects = [question.subject for question in questions_upload_obj]
        subject_instances = await subject_service.create_bulk(subjects)
        subject_uuids = {subject.name: subject.uuid for subject in subject_instances}

        # Fetch the subject_uuid from the database
        language_service = LanguageService(session=self.session)
        languages = [question.language for question in questions_upload_obj]
        language_instances = await language_service.create_bulk(languages)
        language_uuids = {language.name: language.uuid for language in language_instances}

        questions = [
            QuestionsCreateSchema(
                **question.dict(),
                subject_id=subject_uuids[question.subject],
                language_id=language_uuids[question.language]
            )
            for question in questions_upload_obj
        ]

        # Add passage to the database
        passages = {question.passage for question in questions_upload_obj if question.passage}
        if passages != {None}:
            # Add the unique passages to the table and retrieve the uuid of the existing ones.
            passage_service = PassagesService(session=self.session)
            passage_instances = await passage_service.create_bulk(
                [PassagesCreateUpdateSchema(passage_text=passage) for passage in passages]
            )
            passage_uuids = {passage.passage_text: passage.uuid for passage in passage_instances}

            # Update the questions with the passage_uuid
            for question, passage in zip(questions, questions_upload_obj):
                if passage.passage:
                    question.passage_id = passage_uuids[passage.passage]

        # Now we'll check if the tags are present in the database
        tags = [
            TagsCreateUpdateSchema(tag_name=tag, subject_id=subject_uuids[question.subject])
            for question in questions_upload_obj
            for tag in question.tags
        ]
        if tags:
            tag_service = TagsService(session=self.session)
            tags_instances = await tag_service.create_bulk(tags)
            tags_uuids = {tag.tag_name: tag.uuid for tag in tags_instances}

            question_instances = await super().create_bulk(questions)

            # Add these tags to the question
            question_tags_service = QuestionTagsService(session=self.session)
            question_tags = [
                QuestionTagsCreateUpdateSchema(question_id=question.uuid, tag_id=tags_uuids[tag])
                for question, tag in zip(question_instances, questions_upload_obj)
                for tag in questions_upload_obj[question_instances.index(question)].tags
            ]
            await question_tags_service.create_bulk(question_tags)
        else:
            # Add the questions to the database
            question_instances = await super().create_bulk(questions)

        # Add answer in bulk based on type, for this, group the questions based on type
        type_question_dict = {}
        for idx, question in enumerate(questions_upload_obj):
            type_question_dict.setdefault(question.question_type, []).append((question_instances[idx].uuid, question))

        for question_type, question_data in type_question_dict.items():
            if question_type == QuestionTypeEnum.MCQ or question_type == QuestionTypeEnum.MSQ:
                options = [
                    OptionsCreateSchema(question_id=question[0], **option.dict())
                    for question in question_data
                    for option in question[1].options
                ]

                options_service = OptionsService(session=self.session)
                await options_service.create_bulk(options)

            elif question_type == QuestionTypeEnum.NAT:
                answers = [
                    RangeAnswerCreateSchema(question_id=question[0], **question[1].answer.dict())
                    for question in question_data
                ]

                range_answer_service = RangeAnswersService(session=self.session)
                await range_answer_service.create_bulk(answers)
        # Else is not required as currently we only have 3 types of questions - MCQ, MSQ, NAT

        return question_instances

    # Get Functions

    async def get_for_cbt(self, question_uuids: List[UUID]) -> List[QuestionsResponseSchema]:
        """
        This function return questions in the CBTQuestionsResponseSchema
        i.e. it contains, question, options, and passage text (if question is a passage)
        :param question_uuids: UUIDs of the questions
        :return: CBTQuestionsResponseSchema object
        """
        question_instances = await self.get_by_uuids(question_uuids)

        if len(question_instances) != len(question_uuids):
            error_message = "Some of the questions are missing from the database."
            raise DataLogicException(error_message, question_uuids=question_uuids)

        response_dict = {
            question_instance.uuid: QuestionsResponseSchema.from_orm(question_instance)
            for question_instance in question_instances
        }

        # Fetch the options for the questions
        options_service = OptionsService(session=self.session)
        options_instances = await options_service.filter([OptionsModel.question_id.in_(question_uuids)])

        # Populate the options in the response_dict
        for options_instance in options_instances:
            response_dict[options_instance.question_id].options.append(
                CBTOptionsResponseSchema.from_orm(options_instance)
            )

        # Fetch the passage for the questions
        passage_uuid_dict = {
            question_instance.passage_id: question_instance.uuid
            for question_instance in question_instances
            if question_instance.passage_id
        }

        passage_service = PassagesService(session=self.session)
        passage_instances = await passage_service.filter([PassagesModel.uuid.in_(list(passage_uuid_dict.keys()))])

        # Populate the passage in the response_dict
        for passage_instance in passage_instances:
            response_dict[passage_uuid_dict[passage_instance.uuid]].passage = passage_instance.passage_text

        # Response with the order of the question_uuids
        return [response_dict[question_uuid] for question_uuid in question_uuids]

    async def get_solution(self, question_uuids: List[UUID]) -> Dict[UUID, List]:
        """
        This function returns the solution of the questions.
        If it's a MCQ/MSQ type question, it'll return the correct options.
        If it's a NAT type question, it'll return the range of the answer.
        :param question_uuids: UUIDs of the questions
        :return: A dict with question_uuid as key and answer/correct options list as value
        """
        question_instances = await self.get_by_uuids(question_uuids)

        if len(question_instances) != len(question_uuids):
            error_message = "Some of the questions are missing from the database."
            raise DataLogicException(error_message, question_uuids=question_uuids)

        response_dict = {}

        options_service = OptionsService(session=self.session)
        options_instances = await options_service.filter([OptionsModel.question_id.in_(question_uuids)])

        range_answer_service = RangeAnswersService(session=self.session)
        range_answer_instances = await range_answer_service.filter([RangeAnswersModel.question_id.in_(question_uuids)])

        for option_instance in options_instances:
            if option_instance.is_correct_option:
                response_dict.setdefault(option_instance.question_id, []).append(option_instance.uuid)

        for range_answer_instance in range_answer_instances:
            if response_dict.get(range_answer_instance.question_id):
                raise DataLogicException(
                    "Question has both MCQ/MSQ and NAT type answers.",
                    question_uuid=range_answer_instance.question_id,
                )

            response_dict[range_answer_instance.question_id] = [range_answer_instance.start, range_answer_instance.end]

        return response_dict

    # Update Functions

    async def update(self, question_uuid: UUID, question_data: CBTQuestionUpdateSchema) -> QuestionsModel:
        """
        This function allows us to update the question in the database.
        - If the subject is not present in the database, it will create a new subject.
        - If the tags are not present in the database, it will create new tags.

        :param question_uuid: UUID of the question to be updated
        :param question_data: Data to be updated in the database
        :return: Question Model
        """
        # Fetch the question instance from the database
        question_instance = await self.get(question_uuid)
        updated_instance = question_instance

        # Update the instance with the new data
        for key, value in question_data.dict(exclude_unset=True).items():
            if hasattr(updated_instance, key):
                setattr(updated_instance, key, value)

        # Fetch the subject_uuid from the database
        subject = question_data.subject
        if subject:
            subject_service = SubjectsService(session=self.session)
            subject_instance = await subject_service.create(subject)
            subject_uuid = subject_instance.uuid
            updated_instance.subject_id = subject_uuid

        # Fetch the language from the database
        language = question_data.language
        if language:
            language_service = LanguageService(session=self.session)
            language_instance = await language_service.create(language)
            language_uuid = language_instance.uuid
            updated_instance.language_id = language_uuid

        # Add passage to the database
        if question_data.passage:
            passage_service = PassagesService(session=self.session)
            passage_instance = await passage_service.create(
                PassagesCreateUpdateSchema(passage_text=question_data.passage)
            )
            updated_instance.passage_id = passage_instance.uuid
            updated_instance.content_type = ContentTypeEnum.PASSAGE
        elif question_data.content_type == ContentTypeEnum.NORMAL:
            updated_instance.passage_id = None
            updated_instance.content_type = ContentTypeEnum.NORMAL

        # Now we'll check if the tags are present in the database
        tags = question_data.tags
        if tags:
            tag_service = TagsService(session=self.session)
            tags_instances = await tag_service.create_bulk(
                [TagsCreateUpdateSchema(tag_name=tag, subject_id=updated_instance.subject_id) for tag in tags]
            )

            # Add the question to the database
            updated_question_instance = await super().update(
                question_instance, QuestionsUpdateSchema.from_orm(updated_instance)
            )

            # Add these tags to the question
            question_tags_service = QuestionTagsService(session=self.session)
            await question_tags_service.create_bulk(
                [
                    QuestionTagsCreateUpdateSchema(question_id=question_instance.uuid, tag_id=tag_instance.uuid)
                    for tag_instance in tags_instances
                ]
            )
        else:
            # Add the question to the database
            updated_question_instance = await super().update(
                question_instance, QuestionsUpdateSchema.from_orm(updated_instance)
            )

        return updated_question_instance


class SubjectsService(BaseService[SubjectsModel, SubjectsCreateSchema, SubjectsUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=SubjectsModel, **kwargs)

    async def create(self, subject_name: str) -> SubjectsModel:
        """
        This function allows us to add a new subject in the database.

        :param subject_name: Name of the subject.
        :return: Subject Model
        """
        # Check if the subject is already present or not
        subject_instance = await self.filter([self.model.name == subject_name])

        # If the subject is not present in the database, we'll create a new subject
        if not subject_instance:
            subject_instance = await super().create(SubjectsCreateSchema(name=subject_name))
        else:
            subject_instance = subject_instance[0]

        return subject_instance

    async def create_bulk(self, subjects: List[str]) -> List[SubjectsModel]:
        """
        This function allows us to add multiple subjects in the database.

        :param subjects: List of subjects to be added
        :return: List of Subject Models
        """
        # Check if the subjects are already present in the database
        subjects_instances = await self.filter([self.model.name.in_(subjects)])

        # If the subjects are not present in the database, we'll create new subjects
        new_subject_names = set(subjects) - set([subject.name for subject in subjects_instances])
        new_subjects_instances = await super().create_bulk(
            [SubjectsCreateSchema(name=subject_name) for subject_name in new_subject_names]
        )

        # Arrange the result in the order of the subjects requested
        return helper_functions.order_result(subjects_instances + new_subjects_instances, subjects, "name")


class PassagesService(BaseService[PassagesModel, PassagesCreateUpdateSchema, PassagesCreateUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=PassagesModel, **kwargs)

    async def create(self, passage: PassagesCreateUpdateSchema) -> PassagesModel:
        """
        This function allows us to add a new passage in the database.

        :param passage: Text of the passage.
        :return: Passage Model
        """
        # Check if the passage is already present or not
        passage_instance = await self.filter([self.model.passage_text == passage.passage_text])

        # If the passage is not present in the database, we'll create a new passage
        if not passage_instance:
            passage_instance = await super().create(passage)
        else:
            passage_instance = passage_instance[0]

        return passage_instance

    async def create_bulk(self, passages: List[PassagesCreateUpdateSchema]) -> List[PassagesModel]:
        """
        This function allows us to add multiple passages in the database.

        :param passages: List of passages to be added
        :return: List of Passage Models
        """
        passages_text = [passage.passage_text for passage in passages]

        # Check if the passages are already present in the database
        passages_instances = await self.filter([self.model.passage_text.in_(passages_text)])

        # If the passages are not present in the database, we'll create new passages
        new_passage_texts = set(passages_text) - set([passage.passage_text for passage in passages_instances])
        new_passages_instances = await super().create_bulk(
            [PassagesCreateUpdateSchema(passage_text=passage_text) for passage_text in new_passage_texts]
        )

        # Arrange the result in the order of the passages requested
        return helper_functions.order_result(passages_instances + new_passages_instances, passages_text, "passage_text")


class TagsService(BaseService[TagsModel, TagsCreateUpdateSchema, TagsCreateUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(model=TagsModel, **kwargs)

    async def create_bulk(self, tags: List[TagsCreateUpdateSchema]) -> List[TagsModel]:
        """
        This function allows us to add new tags in the database.

        :param tags: List of tags to be added
        :return: Tag Model
        """
        tag_names = [tag.tag_name for tag in tags]
        # Check if the tags are already present in the database
        # We are not raising error as new questions can have old tags as well
        existing_tag_instances = await self.filter([self.model.tag_name.in_(tag_names)])

        if existing_tag_instances:
            # From the tags, remove all the tags that are already present in the database
            existing_tag_names = {tag.tag_name for tag in existing_tag_instances}
            tags = [tag for tag in tags if tag.tag_name not in existing_tag_names]

        new_tags_instances = await super().create_bulk(tags)

        # Arrange the result in the order of the tags requested
        return helper_functions.order_result(existing_tag_instances + new_tags_instances, tag_names, "tag_name")


class QuestionTagsService(
    BaseService[QuestionTagsModel, QuestionTagsCreateUpdateSchema, QuestionTagsCreateUpdateSchema]
):
    def __init__(self, **kwargs):
        super().__init__(QuestionTagsModel, **kwargs)

    async def create_bulk(self, question_tags: List[QuestionTagsCreateUpdateSchema]) -> List[QuestionTagsModel]:
        """
        This function allows us to add tags to a question in the database.
        Note that pair of question_id and tag_id should be unique. Also, some of the tags might be already present

        :param question_tags: List of Question-Tags to be added
        :return: List of QuestionTag Models
        """
        # Fetch the instances that already exists in the database for question_ids
        existing_question_tags_instances = await self.filter(
            [self.model.question_id.in_([question_tag.question_id for question_tag in question_tags])]
        )

        if existing_question_tags_instances:
            # From the question_tags, remove all the question_tags that are already present in the database
            existing_question_tags_tuple = {
                (question_tag.question_id, question_tag.tag_id) for question_tag in existing_question_tags_instances
            }
            new_question_tags = [
                question_tag
                for question_tag in question_tags
                if (question_tag.question_id, question_tag.tag_id) not in existing_question_tags_tuple
            ]
        else:
            new_question_tags = question_tags

        # Create new question_tags
        new_question_tags_instances = await super().create_bulk(new_question_tags)

        # Create a dictionary for quick lookup of instances
        instance_dict = {
            (instance.question_id, instance.tag_id): instance
            for instance in existing_question_tags_instances + new_question_tags_instances
        }

        # Order the result based on the order of the question_tags
        result = [instance_dict[(question_tag.question_id, question_tag.tag_id)] for question_tag in question_tags]

        return result


class OptionsService(BaseService[OptionsModel, OptionsCreateSchema, OptionsUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(OptionsModel, **kwargs)

    async def create_bulk(self, options: List[OptionsCreateSchema]) -> List[OptionsModel]:
        """
        This function allows us to upload multiple options in the database.
        - Can be used for MCQ/MSQ type questions.
        Note that: DataLogicException is expected to be handled outside the function.
            If not, it'll raise HTTP 400 Bad Request with the message.

        :param options: List of OptionsCreateSchema to be uploaded
        :return: List of Option Models
        """
        # Check if options are already present for the question
        options_instances = await self.filter([self.model.question_id.in_(option.question_id for option in options)])

        # If options are already present, we'll raise an exception as we are creating new options
        if options_instances:
            raise DataLogicException(
                "Options are already present for the question(s).",
                question_uuids=[option.question_id for option in options_instances],
            )

        group = {}
        # Group the options based on the question_uuid
        for option in options:
            group.setdefault(option.question_id, []).append(option)

        for key, value in group.items():
            # Check if there are more than 1 options
            if len(value) <= 1:
                raise DataLogicException("At least two options should be present.", question_uuid=key, options=value)

            # Check if any option is correct or not
            if not any([option.is_correct_option for option in value]):
                raise DataLogicException("At least one option should be correct.", question_uuid=key, options=value)

            # Check if order is unique
            if len(set([option.option_order for option in value])) != len(value):
                raise DataLogicException("Order of options should be unique.", question_uuid=key, options=value)

        # Create new options
        options_instances = await super().create_bulk(options)

        return options_instances


class RangeAnswersService(BaseService[RangeAnswersModel, RangeAnswerCreateSchema, RangeAnswerUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(RangeAnswersModel, **kwargs)

    async def create(self, range_answer: RangeAnswerCreateSchema) -> RangeAnswersModel:
        """
        This function allows us to upload a range answer in the database.
        - Can be used for value problems.

        :param range_answer: RangeAnswerCreateSchema to be uploaded
        :return: RangeAnswer Model
        """
        # Check if the answer is already present for the question
        answer_instance = await self.filter([self.model.question_id == range_answer.question_id])

        # If answer is already present, we'll raise an exception as we are creating new answer
        if answer_instance:
            raise DataLogicException(
                "Range Answer is already present for the question.", question_uuid=range_answer.question_id
            )

        # Create new answer
        answer_instance = await super().create(range_answer)

        return answer_instance

    async def create_bulk(self, range_answers: List[RangeAnswerCreateSchema]) -> List[RangeAnswersModel]:
        """
        This function allows us to upload multiple range answers in the database.
        :param range_answers: List of RangeAnswerCreateSchema to be uploaded
        :return: List of RangeAnswer Model
        """
        # Check if the answer is already present for the question
        answer_instances = await self.filter(
            [self.model.question_id.in_([range_answer.question_id for range_answer in range_answers])]
        )

        # If answer is already present, we'll raise an exception as we are creating new answer
        if answer_instances:
            raise DataLogicException(
                "Range Answer is already present for the question.",
                question_uuid=[range_answer.question_id for range_answer in answer_instances],
            )

        # Create new answer
        answer_instances = await super().create_bulk(range_answers)

        return answer_instances


class LanguageService(BaseService[LanguageModel, LanguageCreateUpdateSchema, LanguageCreateUpdateSchema]):
    def __init__(self, **kwargs):
        super().__init__(LanguageModel, **kwargs)

    async def create(self, language_name: LanguageEnum) -> SubjectsModel:
        """
        This function allows us to add a new language in the database.

        :param language_name: Name of the Language (Hindi, English, ...).
        :return: Language Model
        """
        # Check if the language is already present or not
        language_instance = await self.filter([self.model.name == language_name])

        # If the language is not present in the database, we'll create a new language
        if language_instance:
            return language_instance[0]

        return await super().create(LanguageCreateUpdateSchema(name=language_name))

    async def create_bulk(self, languages: List[LanguageEnum]) -> List[SubjectsModel]:
        """
        This function allows us to add multiple languages in the database.

        :param languages: List of languages to be added
        :return: List of Languages Models
        """
        # Check if the languages are already present in the database
        languages_instances = await self.filter([self.model.name.in_(languages)])

        # If the subjects are not present in the database, we'll create new languages
        new_language_names = set(languages) - set([language.name for language in languages_instances])
        new_languages_instances = await super().create_bulk(
            [LanguageCreateUpdateSchema(name=language_name) for language_name in new_language_names]
        )

        # Arrange the result in the order of the subjects requested
        return helper_functions.order_result(languages_instances + new_languages_instances, languages, "name")
