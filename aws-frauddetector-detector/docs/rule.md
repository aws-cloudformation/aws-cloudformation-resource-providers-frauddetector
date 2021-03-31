# AWS::FraudDetector::Detector Rule

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "<a href="#ruleid" title="RuleId">RuleId</a>" : <i>String</i>,
    "<a href="#ruleversion" title="RuleVersion">RuleVersion</a>" : <i>String</i>,
    "<a href="#detectorid" title="DetectorId">DetectorId</a>" : <i>String</i>,
    "<a href="#expression" title="Expression">Expression</a>" : <i>String</i>,
    "<a href="#language" title="Language">Language</a>" : <i>String</i>,
    "<a href="#outcomes" title="Outcomes">Outcomes</a>" : <i>[ <a href="outcome.md">Outcome</a>, ... ]</i>,
    "<a href="#arn" title="Arn">Arn</a>" : <i>String</i>,
    "<a href="#description" title="Description">Description</a>" : <i>String</i>,
    "<a href="#tags" title="Tags">Tags</a>" : <i>[ <a href="tag.md">Tag</a>, ... ]</i>,
    "<a href="#createdtime" title="CreatedTime">CreatedTime</a>" : <i>String</i>,
    "<a href="#lastupdatedtime" title="LastUpdatedTime">LastUpdatedTime</a>" : <i>String</i>
}
</pre>

### YAML

<pre>
<a href="#ruleid" title="RuleId">RuleId</a>: <i>String</i>
<a href="#ruleversion" title="RuleVersion">RuleVersion</a>: <i>String</i>
<a href="#detectorid" title="DetectorId">DetectorId</a>: <i>String</i>
<a href="#expression" title="Expression">Expression</a>: <i>String</i>
<a href="#language" title="Language">Language</a>: <i>String</i>
<a href="#outcomes" title="Outcomes">Outcomes</a>: <i>
      - <a href="outcome.md">Outcome</a></i>
<a href="#arn" title="Arn">Arn</a>: <i>String</i>
<a href="#description" title="Description">Description</a>: <i>String</i>
<a href="#tags" title="Tags">Tags</a>: <i>
      - <a href="tag.md">Tag</a></i>
<a href="#createdtime" title="CreatedTime">CreatedTime</a>: <i>String</i>
<a href="#lastupdatedtime" title="LastUpdatedTime">LastUpdatedTime</a>: <i>String</i>
</pre>

## Properties

#### RuleId

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### RuleVersion

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### DetectorId

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Expression

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Language

_Required_: No

_Type_: String

_Allowed Values_: <code>DETECTORPL</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Outcomes

_Required_: No

_Type_: List of <a href="outcome.md">Outcome</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Arn

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Description

The description.

_Required_: No

_Type_: String

_Minimum_: <code>1</code>

_Maximum_: <code>256</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Tags

_Required_: No

_Type_: List of <a href="tag.md">Tag</a>

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

