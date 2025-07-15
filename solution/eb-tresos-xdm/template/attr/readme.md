# XDM Attributes Documentation

## a:a (Standard Attributes)

### Common Attributes
- name: String
  - "UUID": Unique identifier value (format: "ECUC:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")
  - "DESC": Description text in CDATA section
  - "RELEASE": Release version (e.g., "asc:4.2")
  - "ADMIN-DATA": Administrative data container
  - "POSTBUILDVARIANTSUPPORT": Boolean flag
  - "LOWER-MULTIPLICITY": Integer value for minimum multiplicity
  - "UPPER-MULTIPLICITY": Integer value for maximum multiplicity
  - "SCOPE": Scope specification (e.g., "LOCAL")
  - "ORIGIN": Origin source (e.g., "AUTOSAR_ECUC", "NXP")
  - "SYMBOLICNAMEVALUE": Boolean flag
  - "IMPLEMENTATIONCONFIGCLASS": Configuration class specification
  - "EDITABLE": XPath condition for editability
  - "LABEL": Display label text
  - "OPTIONAL": Boolean flag indicating if element is optional
  - "POSTBUILDVARIANTVALUE": Boolean flag
  - "POSTBUILDVARIANTMULTIPLICITY": Boolean flag

### Type-specific values
- type: String
  - "ADMIN-DATA": Administrative data type
  - "IMPLEMENTATIONCONFIGCLASS": Implementation configuration class type
  - "IDENTIFIABLE": For identifiable containers
  - "MAP": For map type lists
  - "ENUMERATION": For enumeration variables
  - "INTEGER": For integer variables
  - "BOOLEAN": For boolean variables
  - "STRING": For string variables
  - "FUNCTION-NAME": For function pointer variables
  - "SYMBOLIC-NAME-REFERENCE": For references to other elements

## a:da (Default/Range Attributes)

### Common Attributes
- name: String
  - "DEFAULT": Default value specification (can use XPath expression)
  - "RANGE": Valid value range or enumeration list
  - "MIN": Minimum value/count
  - "MAX": Maximum value/count
  - "READONLY": Boolean flag for read-only status
  - "INVALID": Validation rules
  - "EDITABLE": Editability conditions
  - "REF": Reference path specification

### Type-specific values
- type: String
  - "Range": Numerical range validation
  - "XPath": XPath expression validation
  - "INVALID": Invalid value conditions

## a:tst (Test/Validation Rules)

### Attributes
- expr: String (XPath expression for validation)
  Examples:
  - Numeric comparisons: 
    ```xml
    <a:tst expr="&lt;=255"/>
    <a:tst expr="&gt;=0"/>
    ```
  - Existence checks:
    ```xml
    <a:tst expr="node:exists(../AdcChannelLimitCheck)"/>
    ```
  - Uniqueness validations:
    ```xml
    <a:tst expr="text:uniq(../../*/AdcChannelId, .)"/>
    ```
  - Complex conditions:
    ```xml
    <a:tst expr="(. &gt;= 0) and (. &lt; num:i(count(node:current()/../../*)))"/>
    ```

### Message Attributes
- true/false: String
  - Error message when condition matches (true) or doesn't match (false)
  - Example: `false="Duplicate physical channel"`

## a:ref (Reference Attributes)

### Common Attributes
- type: String
  - "REFERENCE": Basic reference type
  - "CHOICE-REFERENCE": Reference with choices
  - "FOREIGN-REFERENCE": Reference to external elements
  - "MODULE-REF": Reference to module definitions
  - "REFINED-MODULE-DEF": Reference to refined module definitions

### Reference Validation
```xml
<a:da name="REF" value="ASPathDataOfSchema:/AUTOSAR/EcucDefs/Adc/AdcConfigSet/AdcHwUnit/AdcChannel"/>
<a:da name="INVALID" type="XPath">
  <a:tst expr="node:refvalid(.)" false="Invalid or empty reference."/>
</a:da>
```

## a:v (Value Elements)

### Usage Types
- Plain text values
- CDATA sections for formatted/multiline content
  ```xml
  <a:v><![CDATA[EN:<html><p>Description text here</p></html>]]></a:v>
  ```
- Language-specific content with HTML formatting

## icc:v (Implementation Config Class Values)

### Common Attributes
- class: String
  - "PreCompile": Pre-compilation configuration
  - "PostBuild": Post-build configuration
  - "PublishedInformation": Published information
- mclass: String (Module configuration)
  - Same values as class but for module-level settings
- vclass: String (Variant configuration)
  - Same values as class but for variant-specific settings

## Usage Notes

1. UUID Format
   - Always follows pattern: "ECUC:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
   - Must be unique within the configuration

2. XPath Functions Commonly Used
   - node:exists(): Check element existence
   - node:current(): Get current node
   - node:refs(): Get referenced elements
   - node:fallback(): Provide default value
   - text:uniq(): Check uniqueness
   - num:i(): Convert to integer

3. EDITABLE Conditions
   ```xml
   <a:a name="EDITABLE" type="XPath">
     <a:tst expr="../../AdcGeneral/AdcGrpNotifCapability = 'true'"/>
   </a:a>
   ```

4. Administrative Data Structure
   ```xml
   <a:a name="ADMIN-DATA" type="ADMIN-DATA">
     <ad:ADMIN-DATA>
       <ad:DOC-REVISIONS>
         <ad:DOC-REVISION>
           <ad:REVISION-LABEL>4.6.0</ad:REVISION-LABEL>
           <ad:ISSUED-BY>AUTOSAR</ad:ISSUED-BY>
           <ad:DATE>2014-10-31</ad:DATE>
         </ad:DOC-REVISION>
       </ad:DOC-REVISIONS>
     </ad:ADMIN-DATA>
   </a:a>
   ```

5. Common Validation Patterns
   - Range checks
   - Cross-reference validations
   - Dependency checks
   - Uniqueness validations
   - Configuration compatibility checks

6. Dependency Management
   - Use XPath expressions for complex dependencies
   - Chain multiple conditions with boolean operators
   - Reference parent/sibling elements for context
   - Handle optional elements with node:exists()
