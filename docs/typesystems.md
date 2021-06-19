# Typesystems

1. If a class has `Q_ENUM()` enum, then functions `qt_getEnumMetaObject` and `qt_getEnumName` should be rejected:

```xml
<rejection class="Quotient" function-name="qt_getEnumMetaObject"/>
<rejection class="Quotient" function-name="qt_getEnumName"/>
```

It's not needed for common enums.

2. If you use QtNetwork in bindings, you need also to include `QHstsPolicy` in `bindings.h`. See [PYSIDE-711](https://bugreports.qt.io/browse/PYSIDE-711) for details.

```c
#include <QtNetwork/QHstsPolicy>
```

3. If you need type with angle brackets in its name, use `&lt;` and `&gt;`:

```xml
<property name="ignoredSslErrors" type="QList&lt;QSslError&gt;" get="ignoredSslErrors" />
```