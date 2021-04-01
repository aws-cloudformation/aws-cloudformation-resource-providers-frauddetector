# AWS::FraudDetector::Detector EventType

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "<a href="#name" title="Name">Name</a>" : <i>String</i>,
    "<a href="#inline" title="Inline">Inline</a>" : <i>Boolean</i>,
    "<a href="#tags" title="Tags">Tags</a>" : <i>[ <a href="tag.md">Tag</a>, ... ]</i>,
    "<a href="#description" title="Description">Description</a>" : <i>String</i>,
    "<a href="#eventvariables" title="EventVariables">EventVariables</a>" : <i>[ <a href="eventvariable.md">EventVariable</a>, ... ]</i>,
    "<a href="#labels" title="Labels">Labels</a>" : <i>[ <a href="label.md">Label</a>, ... ]</i>,
    "<a href="#entitytypes" title="EntityTypes">EntityTypes</a>" : <i>[ <a href="entitytype.md">EntityType</a>, ... ]</i>,
    "<a href="#arn" title="Arn">Arn</a>" : <i>String</i>,
    "<a href="#createdtime" title="CreatedTime">CreatedTime</a>" : <i>String</i>,
    "<a href="#lastupdatedtime" title="LastUpdatedTime">LastUpdatedTime</a>" : <i>String</i>
}
</pre>

### YAML

<pre>
<a href="#name" title="Name">Name</a>: <i>String</i>
<a href="#inline" title="Inline">Inline</a>: <i>Boolean</i>
<a href="#tags" title="Tags">Tags</a>: <i>
      - <a href="tag.md">Tag</a></i>
<a href="#description" title="Description">Description</a>: <i>String</i>
<a href="#eventvariables" title="EventVariables">EventVariables</a>: <i>
      - <a href="eventvariable.md">EventVariable</a></i>
<a href="#labels" title="Labels">Labels</a>: <i>
      - <a href="label.md">Label</a></i>
<a href="#entitytypes" title="EntityTypes">EntityTypes</a>: <i>
      - <a href="entitytype.md">EntityType</a></i>
<a href="#arn" title="Arn">Arn</a>: <i>String</i>
<a href="#createdtime" title="CreatedTime">CreatedTime</a>: <i>String</i>
<a href="#lastupdatedtime" title="LastUpdatedTime">LastUpdatedTime</a>: <i>String</i>
</pre>

## Properties

#### Name

The name for the event type

_Required_: No

_Type_: String

_Minimum_: <code>1</code>

_Maximum_: <code>64</code>

_Pattern_: <code>^[0-9a-z_-]+$</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Inline

_Required_: No

_Type_: Boolean

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Tags

_Required_: No

_Type_: List of <a href="tag.md">Tag</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Description

The description of the event type.

_Required_: No

_Type_: String

_Minimum_: <code>1</code>

_Maximum_: <code>128</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### EventVariables

_Required_: No

_Type_: List of <a href="eventvariable.md">EventVariable</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Labels

_Required_: No

_Type_: List of <a href="label.md">Label</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### EntityTypes

_Required_: No

_Type_: List of <a href="entitytype.md">EntityType</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Arn

The ARN of the event type.

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### CreatedTime

The time when the event type was created.

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### LastUpdatedTime

The time when the event type was last updated.

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)
