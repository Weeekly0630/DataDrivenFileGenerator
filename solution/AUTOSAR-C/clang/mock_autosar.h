// mock_autosar.h - Minimal AUTOSAR macro/type/struct mocks for Clang AST testing
#ifndef MOCK_AUTOSAR_H
#define MOCK_AUTOSAR_H

#define FUNC(rettype, memclass) rettype
#define CONST(type, memclass) type
#define P2CONST(type, memclass, ptrclass) const struct type *
#define P2VAR(type, memclass, ptrclass) struct type *
#define VAR(type, memclass) type
#define AUTOMATIC
#define I2C_APPL_CONST
#define I2C_APPL_DATA
#define I2C_CODE

#endif // MOCK_AUTOSAR_H
