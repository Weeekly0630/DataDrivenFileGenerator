# XDM Variable Tags Documentation

## v:ctr (Container Tags)

### Common Attributes

- type: String
  - "IDENTIFIABLE": For identifiable containers
  - "MAP": For map type containers
  - "MODULE-DEF": For module definition containers 
  - "AR-PACKAGE": For AUTOSAR package containers
  - "AR-ELEMENT": For AUTOSAR element containers
- name: String - Container name identifier
- Optional a:a attributes:
  - "UUID": Unique identifier
  - "DESC": Description in CDATA format
  - "IMPLEMENTATIONCONFIGCLASS": Implementation class specification
  - "POSTBUILDVARIANTVALUE": Boolean
  - "OPTIONAL": Boolean indicating if container is optional
  - "ORIGIN": Source of definition (e.g., "AUTOSAR_ECUC", "NXP")
  - "SCOPE": Scope specification (e.g., "LOCAL")
  - "LABEL": Display label text

### Example
```xml
<v:ctr name="AdcConfigSet" type="IDENTIFIABLE">
  <a:a name="DESC">
    <a:v><![CDATA[Description text]]></a:v>
  </a:a>
  <a:a name="UUID" value="ECUC:xxx-xxx"/>
  <a:a name="IMPLEMENTATIONCONFIGCLASS" type="IMPLEMENTATIONCONFIGCLASS">
    <icc:v mclass="PreCompile">VariantPostBuild</icc:v>
  </a:a>
</v:ctr>
```

## v:var (Variable Tags)

### Attributes
- name: String - Variable name identifier
- type: String - Data type
  - "INTEGER": For numeric values
  - "BOOLEAN": For true/false values
  - "ENUMERATION": For enumerated values 
  - "FUNCTION-NAME": For function references
  - "STRING": For text values
  - "INTEGER_LABEL": For labeled integer values
  - "BOOLEAN_LABEL": For labeled boolean values
  - "STRING_LABEL": For labeled string values

### Data Validation
- Using a:da tags:
  - "DEFAULT": Default value or XPath expression
  - "RANGE": Valid value range or enumeration list
  - "MIN"/"MAX": Minimum/maximum values
  - "INVALID": Invalid value conditions
  - "EDITABLE": Editability conditions using XPath
  - "READONLY": Boolean flag for read-only status
  - "REF": Reference path specification

### Special Validation
- Default value from XPath:
```xml
<a:da name="DEFAULT" type="XPath" 
      expr="concat('ADC', string(node:fallback(node:current()/../@index,'0')))"/>
```

- Complex range validation:
```xml
<a:da name="RANGE" type="XPath">
  <a:tst expr="(. &gt;= 0) and (. &lt; num:i(count(node:current()/../../*)))"
        false="Value out of range"/>
</a:da>
```

## v:lst (List Tags)

### Attributes
- type: String
  - "MAP": For mapping lists
  - "TOP-LEVEL-PACKAGES": For package listings
  - "ELEMENTS": For element listings
- name: String - List identifier
- Validation rules:
  - MIN/MAX entries using a:da
  - Entry uniqueness constraints
  - Cross-reference validations
  - Maximum count validations

### Example with Complex Validation
```xml
<v:lst name="AdcChannel" type="MAP">
  <a:da name="MIN" value="1"/>
  <a:da name="INVALID" type="XPath">
    <a:tst expr="num:i(count(node:current()/*)) &gt; ecu:get('Adc.MaxChannels')"
          true="Maximum channels exceeded"/>
    <a:tst expr="text:uniq(../*/AdcChannelId, .)" 
          false="Duplicate channel"/>
  </a:da>
</v:lst>
```

## v:ref (Reference Tags)

### Attributes
- name: String - Reference identifier
- type: String
  - "REFERENCE": Basic reference
  - "CHOICE-REFERENCE": Reference with choices
  - "SYMBOLIC-NAME-REFERENCE": Symbolic reference
  - "REFINED-MODULE-DEF": Reference to module definition
  - "MODULE-REF": Reference to module
  - "FOREIGN-REFERENCE": Reference to external elements

### Reference Validation
```xml
<v:ref name="AdcGroupDefinition" type="REFERENCE">
  <a:da name="REF" value="ASPathDataOfSchema:/AUTOSAR/EcucDefs/Adc/AdcConfigSet/AdcChannel"/>
  <a:da name="INVALID" type="XPath">
    <a:tst expr="node:refvalid(.)" false="Invalid reference"/>
    <a:tst expr="contains(., ../../../../@name)"
          false="Must reference same hardware unit"/>
  </a:da>
</v:ref>
```

## Common XPath Functions

- node:exists(): Check element existence
- node:current(): Get current node
- node:refs(): Get referenced elements 
- node:refvalid(): Validate references
- node:fallback(): Provide default value
- text:uniq(): Check uniqueness
- text:split(): Split text
- text:grep(): Search text
- num:i(): Convert to integer
- ecu:get(): Get ECU parameter
- ecu:list(): Get ECU list values

## Implementation Config Classes

- PreCompile: Pre-compilation configuration
- PostBuild: Post-build configuration 
- PublishedInformation: Published information
- Class modifiers:
  - class: Basic class
  - mclass: Module class
  - vclass: Variant class

## Validation Rules

1. Range Checks
```xml
<a:da name="INVALID" type="Range">
  <a:tst expr="&lt;=255"/>
  <a:tst expr="&gt;=0"/>
</a:da>
```

2. Uniqueness
```xml
<a:tst expr="text:uniq(../*/Id, .)" false="Duplicate ID"/>
```

3. Cross-References
```xml
<a:tst expr="node:refvalid(.)" false="Invalid reference"/>
```

4. Conditional Validation
```xml
<a:tst expr="(. = 'true') and (../OtherParam = 'false')" 
      true="Incompatible configuration"/>
```

5. Complex Dependencies
```xml
<a:tst expr="(../../AdcGeneral/AdcEnableLimitCheck = 'true') and 
            (num:i(count(node:current()/*)) &gt; 1) and
            (num:i(count(node:refs(./*)/AdcChannelLimitCheck[.='true'])) = 1)"
      true="Invalid limit check configuration"/>
```

## Common Usage Patterns

### 1. Dependency Chains
```xml
<a:a name="EDITABLE" type="XPath">
  <a:tst expr="node:exists(../AdcChannelLimitCheck) and 
              (../AdcChannelLimitCheck = 'true') and 
              (../../../../../../AdcGeneral/AdcEnableLimitCheck = 'true')"/>
</a:a>
```

### 2. Default Value Generation
```xml
<a:da name="DEFAULT" type="XPath" 
      expr="node:fallback(node:current()/../@index, '0')"/>
```

### 3. Cross-Unit Validation
```xml
<a:da name="INVALID" type="XPath">
  <a:tst expr="(count(node:refs('ASPathDataOfSchema:/Module/Unit')/*) = 0)"
        true="Referenced unit must be configured"/>
</a:da>
```

### 4. Conditional Feature Enablement
```xml
<v:var name="FeatureEnable" type="BOOLEAN">
  <a:da name="EDITABLE" type="XPath" 
        expr="../../../../../NonAutosar/GlobalFeatureEnable = 'true'"/>
  <a:da name="DEFAULT" value="false"/>
</v:var>
```

### 5. Configuration Class Inheritance
```xml
<a:a name="IMPLEMENTATIONCONFIGCLASS" type="IMPLEMENTATIONCONFIGCLASS">
  <icc:v mclass="PreCompile">VariantPostBuild</icc:v>
  <icc:v vclass="PostBuild">VariantPostBuild</icc:v>
</a:a>
```d

### 6. Multi-Level Validation
```xml
<a:da name="INVALID" type="XPath">
  <!-- Hardware capability check -->
  <a:tst expr="(. &gt; ecu:get('MaxChannels'))"
        true="Exceeds hardware capability"/>
  <!-- Functional dependency check -->
  <a:tst expr="(. = 'FEATURE_X') and not(node:exists(../RequiredFeature))"
        true="Required feature not configured"/>
  <!-- Cross-reference integrity -->
  <a:tst expr="node:refs(.)/Status = 'ACTIVE'"
        false="Referenced component must be active"/>
</a:da>
```

### 7. Dynamic Range Generation
```xml
<a:da name="RANGE" type="XPath"
      expr="ecu:list(concat('Module.Unit',
            substring-after(string(node:fallback(../UnitId,'')), 'UNIT'),
            '.ValidValues'))"/>
```

### 8. Nested Container Dependencies
```xml
<v:ctr name="SubFeature" type="IDENTIFIABLE">
  <a:a name="EDITABLE" type="XPath">
    <a:tst expr="../MainFeature/EnableSubFeatures = 'true' and
                  ../../GeneralSettings/AllowSubFeatures = 'true'"/>
  </a:a>
</v:ctr>
```

These patterns demonstrate common ways to handle complex configurations, validations, and dependencies in XDM files while maintaining data integrity and configuration consistency.
