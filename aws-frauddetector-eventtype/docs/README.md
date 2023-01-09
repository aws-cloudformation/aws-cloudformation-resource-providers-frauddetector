# AWS::FraudDetector::EventType

A resource schema for an EventType in Amazon Fraud Detector.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "AWS::FraudDetector::EventType",
    "Properties" : {
        "<a href="#name" title="Name">Name</a>" : <i>String</i>,
        "<a href="#tags" title="Tags">Tags</a>" : <i>[ <a href="tag.md">Tag</a>, ... ]</i>,
        "<a href="#description" title="Description">Description</a>" : <i>String</i>,
        "<a href="#eventvariables" title="EventVariables">EventVariables</a>" : <i>[ <a href="eventvariable.md">EventVariable</a>, ... ]</i>,
        "<a href="#labels" title="Labels">Labels</a>" : <i>[ <a href="label.md">Label</a>, ... ]</i>,
        "<a href="#entitytypes" title="EntityTypes">EntityTypes</a>" : <i>[ <a href="entitytype.md">EntityType</a>, ... ]</i>,
    }
}
</pre>

### YAML

<pre>
Type: AWS::FraudDetector::EventType
Properties:
    <a href="#name" title="Name">Name</a>: <i>String</i>
    <a href="#tags" title="Tags">Tags</a>: <i>
      - <a href="tag.md">Tag</a></i>
    <a href="#description" title="Description">Description</a>: <i>String</i>
    <a href="#eventvariables" title="EventVariables">EventVariables</a>: <i>
      - <a href="eventvariable.md">EventVariable</a></i>
    <a href="#labels" title="Labels">Labels</a>: <i>
      - <a href="label.md">Label</a></i>
    <a href="#entitytypes" title="EntityTypes">EntityTypes</a>: <i>
      - <a href="entitytype.md">EntityType</a></i>
</pre>

## Properties

#### Name

The name for the event type

_Required_: Yes

_Type_: String

_Minimum Length_: <code>1</code>

_Maximum Length_: <code>64</code>

_Pattern_: <code>^[0-9a-z_-]+$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### Tags

Tags associated with this event type.

_Required_: No

_Type_: List of <a href="tag.md">Tag</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Description

The description of the event type.

_Required_: No

_Type_: String

_Minimum Length_: <code>1</code>

_Maximum Length_: <code>128</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### EventVariables

_Required_: Yes

_Type_: List of <a href="eventvariable.md">EventVariable</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Labels

_Required_: Yes

_Type_: List of <a href="label.md">Label</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### EntityTypes

_Required_: Yes

_Type_: List of <a href="entitytype.md">EntityType</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the Arn.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Arn

The ARN of the event type.

#### CreatedTime

The time when the event type was created.

#### LastUpdatedTime

The time when the event type was last updated.

#### Arn

Returns the <code>Arn</code> value.

#### CreatedTime

Returns the <code>CreatedTime</code> value.

#### LastUpdatedTime

Returns the <code>LastUpdatedTime</code> value.

#### Arn

Returns the <code>Arn</code> value.

#### CreatedTime

Returns the <code>CreatedTime</code> value.

#### LastUpdatedTime

Returns the <code>LastUpdatedTime</code> value.

#### Arn

Returns the <code>Arn</code> value.

#### CreatedTime

Returns the <code>CreatedTime</code> value.

#### LastUpdatedTime

Returns the <code>LastUpdatedTime</code> value.
