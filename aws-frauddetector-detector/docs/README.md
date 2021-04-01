# AWS::FraudDetector::Detector

A resource schema for a Detector in Amazon Fraud Detector.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "AWS::FraudDetector::Detector",
    "Properties" : {
        "<a href="#detectorid" title="DetectorId">DetectorId</a>" : <i>String</i>,
        "<a href="#detectorversionstatus" title="DetectorVersionStatus">DetectorVersionStatus</a>" : <i>String</i>,
        "<a href="#ruleexecutionmode" title="RuleExecutionMode">RuleExecutionMode</a>" : <i>String</i>,
        "<a href="#tags" title="Tags">Tags</a>" : <i>[ <a href="tag.md">Tag</a>, ... ]</i>,
        "<a href="#description" title="Description">Description</a>" : <i>String</i>,
        "<a href="#rules" title="Rules">Rules</a>" : <i>[ <a href="rule.md">Rule</a>, ... ]</i>,
        "<a href="#eventtype" title="EventType">EventType</a>" : <i><a href="eventtype.md">EventType</a></i>,
    }
}
</pre>

### YAML

<pre>
Type: AWS::FraudDetector::Detector
Properties:
    <a href="#detectorid" title="DetectorId">DetectorId</a>: <i>String</i>
    <a href="#detectorversionstatus" title="DetectorVersionStatus">DetectorVersionStatus</a>: <i>String</i>
    <a href="#ruleexecutionmode" title="RuleExecutionMode">RuleExecutionMode</a>: <i>String</i>
    <a href="#tags" title="Tags">Tags</a>: <i>
      - <a href="tag.md">Tag</a></i>
    <a href="#description" title="Description">Description</a>: <i>String</i>
    <a href="#rules" title="Rules">Rules</a>: <i>
      - <a href="rule.md">Rule</a></i>
    <a href="#eventtype" title="EventType">EventType</a>: <i><a href="eventtype.md">EventType</a></i>
</pre>

## Properties

#### DetectorId

The ID of the detector

_Required_: Yes

_Type_: String

_Minimum_: <code>1</code>

_Maximum_: <code>64</code>

_Pattern_: <code>^[0-9a-z_-]+$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### DetectorVersionStatus

The desired detector version status for the detector

_Required_: No

_Type_: String

_Allowed Values_: <code>DRAFT</code> | <code>ACTIVE</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### RuleExecutionMode

_Required_: No

_Type_: String

_Allowed Values_: <code>FIRST_MATCHED</code> | <code>ALL_MATCHED</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Tags

Tags associated with this detector.

_Required_: No

_Type_: List of <a href="tag.md">Tag</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Description

The description of the detector.

_Required_: No

_Type_: String

_Minimum_: <code>1</code>

_Maximum_: <code>128</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Rules

_Required_: Yes

_Type_: List of <a href="rule.md">Rule</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### EventType

_Required_: Yes

_Type_: <a href="eventtype.md">EventType</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the Arn.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Arn

The ARN of the detector.

#### DetectorVersionId

The active version ID of the detector

#### CreatedTime

The time when the detector was created.

#### LastUpdatedTime

The time when the detector was last updated.

#### RuleVersion

Returns the <code>RuleVersion</code> value.

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
