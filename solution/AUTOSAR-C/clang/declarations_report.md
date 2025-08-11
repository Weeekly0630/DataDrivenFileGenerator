# C/C++ Code Analysis Report

**Source File:** `test_autosar_minimal.c`

**Generated:** 2025-08-11 15:22:41

---

## Table of Contents
- [Structs](#structs)
- [Unions](#unions)
- [Enums](#enums)
- [Typedefs](#typedefs)
- [Variables](#variables)
- [Functions](#functions)
- [Macros](#macros)

---

## Structs

### `I2c_Ipw_HwChannelConfigType`

**Description:** @brief /

**Location:** `.\test_autosar_minimal.c:37:8`

**Fields:**
| Field Name | Type | Comment |
|------------|------|---------|
| `I2c_Ipw_eChannelType` | `I2c_StatusType` | /**
     * @brief
     *
     */ |
| `I2c_Ipw_LPI2CHwConfig` | `I2c_StatusType` | /**
     * @brief
     *
     */ |
| `I2c_Ipw_FlexIOCHwConfig` | `I2c_StatusType` | /**
     * @brief
     *
     */ |


### `I2c_RequestType`

**Location:** `.\test_autosar_minimal.c:56:8`

**Fields:**
| Field Name | Type | Comment |
|------------|------|---------|
| `u8BufferSize` | `int` | - |

## Unions

*No union declarations found.*

## Enums

*No enum declarations found.*

## Typedefs
| Name | Underlying Type | Comment | Location |
|------|-----------------|---------|----------|
| `uint8` | `unsigned char` | - | `.\test_autosar_minimal.c:25:23` |
| `Std_ReturnType` | `int` | - | `.\test_autosar_minimal.c:26:23` |
| `I2c_HwChannelType` | `int` | - | `.\test_autosar_minimal.c:27:23` |
| `I2c_DataType` | `int` | - | `.\test_autosar_minimal.c:28:23` |
| `I2c_StatusType` | `int` | - | `.\test_autosar_minimal.c:29:23` |

## Variables
| Name | Type | Initializer | Comment | Location |
|------|------|-------------|---------|----------|
| `I2cStatus` | `I2c_StatusType` | `<expression>` | - | `.\test_autosar_minimal.c:31:16` |

## Functions

### `I2c_Ipw_InitChannel`

**Description:** @brief /

**Return Type:** `void`

**Location:** `.\test_autosar_minimal.c:66:1`

**Parameters:**
| Name | Type |
|------|------|
| `u8Channel` | `uint8` |
| `pConfigPtr` | `const struct I2c_Ipw_HwChannelConfigType *` |


### `I2c_Ipw_CheckDataLength`

**Return Type:** `Std_ReturnType`

**Location:** `.\test_autosar_minimal.c:83:1`

**Parameters:**
| Name | Type |
|------|------|
| `pRequest` | `const struct I2c_RequestType *` |
| `eChannelType` | `I2c_HwChannelType` |

## Macros

*No macro definitions found in main file.*
