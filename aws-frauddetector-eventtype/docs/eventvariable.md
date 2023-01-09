# AWS::FraudDetector::EventType EventVariable

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "<a href="#arn" title="Arn">Arn</a>" : <i>String</i>,
    "<a href="#inline" title="Inline">Inline</a>" : <i>Boolean</i>,
    "<a href="#name" title="Name">Name</a>" : <i>String</i>,
    "<a href="#datasource" title="DataSource">DataSource</a>" : <i>String</i>,
    "<a href="#datatype" title="DataType">DataType</a>" : <i>String</i>,
    "<a href="#defaultvalue" title="DefaultValue">DefaultValue</a>" : <i>String</i>,
    "<a href="#variabletype" title="VariableType">VariableType</a>" : <i>String</i>,
    "<a href="#description" title="Description">Description</a>" : <i>String</i>,
    "<a href="#tags" title="Tags">Tags</a>" : <i>[ <a href="tag.md">Tag</a>, ... ]</i>,
    "<a href="#createdtime" title="CreatedTime">CreatedTime</a>" : <i>String</i>,
    "<a href="#lastupdatedtime" title="LastUpdatedTime">LastUpdatedTime</a>" : <i>String</i>
}
</pre>

### YAML

<pre>
<a href="#arn" title="Arn">Arn</a>: <i>String</i>
<a href="#inline" title="Inline">Inline</a>: <i>Boolean</i>
<a href="#name" title="Name">Name</a>: <i>String</i>
<a href="#datasource" title="DataSource">DataSource</a>: <i>String</i>
<a href="#datatype" title="DataType">DataType</a>: <i>String</i>
<a href="#defaultvalue" title="DefaultValue">DefaultValue</a>: <i>String</i>
<a href="#variabletype" title="VariableType">VariableType</a>: <i>String</i>
<a href="#description" title="Description">Description</a>: <i>String</i>
<a href="#tags" title="Tags">Tags</a>: <i>
      - <a href="tag.md">Tag</a></i>
<a href="#createdtime" title="CreatedTime">CreatedTime</a>: <i>String</i>
<a href="#lastupdatedtime" title="LastUpdatedTime">LastUpdatedTime</a>: <i>String</i>
</pre>

## Properties

#### Arn

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Inline

_Required_: No

_Type_: Boolean

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Name

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### DataSource

_Required_: No

_Type_: String

_Allowed Values_: <code>EVENT</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### DataType

_Required_: No

_Type_: String

_Allowed Values_: <code>STRING</code> | <code>INTEGER</code> | <code>FLOAT</code> | <code>BOOLEAN</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### DefaultValue

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### VariableType

_Required_: No

_Type_: String

_Allowed Values_: <code>AUTH_CODE</code> | <code>AVS</code> | <code>BILLING_ADDRESS_L1</code> | <code>BILLING_ADDRESS_L2</code> | <code>BILLING_CITY</code> | <code>BILLING_COUNTRY</code> | <code>BILLING_NAME</code> | <code>BILLING_PHONE</code> | <code>BILLING_STATE</code> | <code>BILLING_ZIP</code> | <code>CARD_BIN</code> | <code>CATEGORICAL</code> | <code>CURRENCY_CODE</code> | <code>EMAIL_ADDRESS</code> | <code>FINGERPRINT</code> | <code>FRAUD_LABEL</code> | <code>FREE_FORM_TEXT</code> | <code>IP_ADDRESS</code> | <code>NUMERIC</code> | <code>ORDER_ID</code> | <code>PAYMENT_TYPE</code> | <code>PHONE_NUMBER</code> | <code>PRICE</code> | <code>PRODUCT_CATEGORY</code> | <code>SHIPPING_ADDRESS_L1</code> | <code>SHIPPING_ADDRESS_L2</code> | <code>SHIPPING_CITY</code> | <code>SHIPPING_COUNTRY</code> | <code>SHIPPING_NAME</code> | <code>SHIPPING_PHONE</code> | <code>SHIPPING_STATE</code> | <code>SHIPPING_ZIP</code> | <code>USERAGENT</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Description

The description.

_Required_: No

_Type_: String

_Minimum Length_: <code>1</code>

_Maximum Length_: <code>256</code>

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
