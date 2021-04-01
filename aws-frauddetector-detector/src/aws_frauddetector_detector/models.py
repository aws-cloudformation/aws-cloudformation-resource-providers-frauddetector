# DO NOT modify this file by hand, changes will be overwritten
import sys
from dataclasses import dataclass
from inspect import getmembers, isclass
from typing import (
    AbstractSet,
    Any,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
)
from cloudformation_cli_python_lib.recast import recast_object
from cloudformation_cli_python_lib.utils import deserialize_list

T = TypeVar("T")


def set_or_none(value: Optional[Sequence[T]]) -> Optional[AbstractSet[T]]:
    if value:
        return set(value)
    return None


@dataclass
class ResourceHandlerRequest(BaseResourceHandlerRequest):
    # pylint: disable=invalid-name
    desiredResourceState: Optional["ResourceModel"]
    previousResourceState: Optional["ResourceModel"]


@dataclass
class ResourceModel(BaseModel):
    DetectorId: Optional[str]
    DetectorVersionStatus: Optional[str]
    DetectorVersionId: Optional[str]
    RuleExecutionMode: Optional[str]
    Tags: Optional[Sequence["_Tag"]]
    Description: Optional[str]
    Rules: Optional[Sequence["_Rule"]]
    EventType: Optional["_EventType"]
    Arn: Optional[str]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_ResourceModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_ResourceModel"]:
        if not json_data:
            return None
        dataclasses = {n: o for n, o in getmembers(sys.modules[__name__]) if isclass(o)}
        recast_object(cls, json_data, dataclasses)
        return cls(
            DetectorId=json_data.get("DetectorId"),
            DetectorVersionStatus=json_data.get("DetectorVersionStatus"),
            DetectorVersionId=json_data.get("DetectorVersionId"),
            RuleExecutionMode=json_data.get("RuleExecutionMode"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            Description=json_data.get("Description"),
            Rules=deserialize_list(json_data.get("Rules"), Rule),
            EventType=EventType._deserialize(json_data.get("EventType")),
            Arn=json_data.get("Arn"),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_ResourceModel = ResourceModel


@dataclass
class Tag(BaseModel):
    Key: Optional[str]
    Value: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_Tag"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_Tag"]:
        if not json_data:
            return None
        return cls(
            Key=json_data.get("Key"),
            Value=json_data.get("Value"),
        )


# work around possible type aliasing issues when variable has same name as a model
_Tag = Tag


@dataclass
class Rule(BaseModel):
    RuleId: Optional[str]
    RuleVersion: Optional[str]
    DetectorId: Optional[str]
    Expression: Optional[str]
    Language: Optional[str]
    Outcomes: Optional[Sequence["_Outcome"]]
    Arn: Optional[str]
    Description: Optional[str]
    Tags: Optional[Sequence["_Tag"]]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_Rule"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_Rule"]:
        if not json_data:
            return None
        return cls(
            RuleId=json_data.get("RuleId"),
            RuleVersion=json_data.get("RuleVersion"),
            DetectorId=json_data.get("DetectorId"),
            Expression=json_data.get("Expression"),
            Language=json_data.get("Language"),
            Outcomes=deserialize_list(json_data.get("Outcomes"), Outcome),
            Arn=json_data.get("Arn"),
            Description=json_data.get("Description"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_Rule = Rule


@dataclass
class Outcome(BaseModel):
    Arn: Optional[str]
    Inline: Optional[bool]
    Name: Optional[str]
    Description: Optional[str]
    Tags: Optional[Sequence["_Tag"]]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_Outcome"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_Outcome"]:
        if not json_data:
            return None
        return cls(
            Arn=json_data.get("Arn"),
            Inline=json_data.get("Inline"),
            Name=json_data.get("Name"),
            Description=json_data.get("Description"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_Outcome = Outcome


@dataclass
class EventType(BaseModel):
    Name: Optional[str]
    Inline: Optional[bool]
    Tags: Optional[Sequence["_Tag"]]
    Description: Optional[str]
    EventVariables: Optional[Sequence["_EventVariable"]]
    Labels: Optional[Sequence["_Label"]]
    EntityTypes: Optional[Sequence["_EntityType"]]
    Arn: Optional[str]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_EventType"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_EventType"]:
        if not json_data:
            return None
        return cls(
            Name=json_data.get("Name"),
            Inline=json_data.get("Inline"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            Description=json_data.get("Description"),
            EventVariables=deserialize_list(json_data.get("EventVariables"), EventVariable),
            Labels=deserialize_list(json_data.get("Labels"), Label),
            EntityTypes=deserialize_list(json_data.get("EntityTypes"), EntityType),
            Arn=json_data.get("Arn"),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_EventType = EventType


@dataclass
class EventVariable(BaseModel):
    Arn: Optional[str]
    Inline: Optional[bool]
    Name: Optional[str]
    DataSource: Optional[str]
    DataType: Optional[str]
    DefaultValue: Optional[str]
    VariableType: Optional[str]
    Description: Optional[str]
    Tags: Optional[Sequence["_Tag"]]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_EventVariable"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_EventVariable"]:
        if not json_data:
            return None
        return cls(
            Arn=json_data.get("Arn"),
            Inline=json_data.get("Inline"),
            Name=json_data.get("Name"),
            DataSource=json_data.get("DataSource"),
            DataType=json_data.get("DataType"),
            DefaultValue=json_data.get("DefaultValue"),
            VariableType=json_data.get("VariableType"),
            Description=json_data.get("Description"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_EventVariable = EventVariable


@dataclass
class Label(BaseModel):
    Arn: Optional[str]
    Inline: Optional[bool]
    Name: Optional[str]
    Description: Optional[str]
    Tags: Optional[Sequence["_Tag"]]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_Label"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_Label"]:
        if not json_data:
            return None
        return cls(
            Arn=json_data.get("Arn"),
            Inline=json_data.get("Inline"),
            Name=json_data.get("Name"),
            Description=json_data.get("Description"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_Label = Label


@dataclass
class EntityType(BaseModel):
    Arn: Optional[str]
    Inline: Optional[bool]
    Name: Optional[str]
    Description: Optional[str]
    Tags: Optional[Sequence["_Tag"]]
    CreatedTime: Optional[str]
    LastUpdatedTime: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_EntityType"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_EntityType"]:
        if not json_data:
            return None
        return cls(
            Arn=json_data.get("Arn"),
            Inline=json_data.get("Inline"),
            Name=json_data.get("Name"),
            Description=json_data.get("Description"),
            Tags=deserialize_list(json_data.get("Tags"), Tag),
            CreatedTime=json_data.get("CreatedTime"),
            LastUpdatedTime=json_data.get("LastUpdatedTime"),
        )


# work around possible type aliasing issues when variable has same name as a model
_EntityType = EntityType
