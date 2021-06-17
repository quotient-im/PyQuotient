# Typesystems

1. If a class has `Q_ENUM()` enum, then functions `qt_getEnumMetaObject` and `qt_getEnumName` should be rejected:

```xml
<rejection class="Quotient" function-name="qt_getEnumMetaObject"/>
<rejection class="Quotient" function-name="qt_getEnumName"/>
```

It's not needed for common enums.
