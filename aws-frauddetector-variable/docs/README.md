# AWS::FraudDetector::Variable

A resource schema for a Variable in Amazon Fraud Detector.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "AWS::FraudDetector::Variable",
    "Properties" : {
        "<a href="#name" title="Name">Name</a>" : <i>String</i>,
        "<a href="#datasource" title="DataSource">DataSource</a>" : <i>String</i>,
        "<a href="#datatype" title="DataType">DataType</a>" : <i>String</i>,
        "<a href="#defaultvalue" title="DefaultValue">DefaultValue</a>" : <i>String</i>,
        "<a href="#description" title="Description">Description</a>" : <i>String</i>,
        "<a href="#tags" title="Tags">Tags</a>" : <i>[ <a href="tag.md">Tag</a>, ... ]</i>,
        "<a href="#variabletype" title="VariableType">VariableType</a>" : <i>String</i>,
    }
}
</pre>

### YAML

<pre>
Type: AWS::FraudDetector::Variable
Properties:
    <a href="#name" title="Name">Name</a>: <i>String</i>
    <a href="#datasource" title="DataSource">DataSource</a>: <i>String</i>
    <a href="#datatype" title="DataType">DataType</a>: <i>String</i>
    <a href="#defaultvalue" title="DefaultValue">DefaultValue</a>: <i>String</i>
    <a href="#description" title="Description">Description</a>: <i>String</i>
    <a href="#tags" title="Tags">Tags</a>: <i>
      - <a href="tag.md">Tag</a></i>
    <a href="#variabletype" title="VariableType">VariableType</a>: <i>String</i>
</pre>

## Properties

#### Name

The name of the variable.

_Required_: Yes

_Type_: String

_Pattern_: <code>^[a-z_][a-z0-9_]{0,99}?$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### DataSource

The source of the data.

_Required_: Yes

_Type_: String

_Allowed Values_: <code>EVENT</code> | <code>EXTERNAL_MODEL_SCORE</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### DataType

The data type.

_Required_: Yes

_Type_: String

_Allowed Values_: <code>STRING</code> | <code>INTEGER</code> | <code>FLOAT</code> | <code>BOOLEAN</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### DefaultValue

The default value for the variable when no value is received.

_Required_: Yes

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

Tags associated with this variable.

_Required_: No

_Type_: List of <a href="tag.md">Tag</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### VariableType

The variable type. For more information see https://docs.aws.amazon.com/frauddetector/latest/ug/create-a-variable.html#variable-types

_Required_: No

_Type_: String

_Allowed Values_: <code>AUTH_CODE</code> | <code>AVS</code> | <code>BILLING_ADDRESS_L1</code> | <code>BILLING_ADDRESS_L2</code> | <code>BILLING_CITY</code> | <code>BILLING_COUNTRY</code> | <code>BILLING_NAME</code> | <code>BILLING_PHONE</code> | <code>BILLING_STATE</code> | <code>BILLING_ZIP</code> | <code>CARD_BIN</code> | <code>CATEGORICAL</code> | <code>CURRENCY_CODE</code> | <code>EMAIL_ADDRESS</code> | <code>FINGERPRINT</code> | <code>FRAUD_LABEL</code> | <code>FREE_FORM_TEXT</code> | <code>IP_ADDRESS</code> | <code>NUMERIC</code> | <code>ORDER_ID</code> | <code>PAYMENT_TYPE</code> | <code>PHONE_NUMBER</code> | <code>PRICE</code> | <code>PRODUCT_CATEGORY</code> | <code>SHIPPING_ADDRESS_L1</code> | <code>SHIPPING_ADDRESS_L2</code> | <code>SHIPPING_CITY</code> | <code>SHIPPING_COUNTRY</code> | <code>SHIPPING_NAME</code> | <code>SHIPPING_PHONE</code> | <code>SHIPPING_STATE</code> | <code>SHIPPING_ZIP</code> | <code>USERAGENT</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the Arn.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Arn

The ARN of the variable.

#### CreatedTime

The time when the variable was created.

#### LastUpdatedTime

The time when the variable was last updated.
