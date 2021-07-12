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

4. [report] Don't create separate typesystem definition file for header-only library. If typesystem is loaded using `<load-typesystem>` shiboken(tested on 6.1.1) expects appropriate module.

5. [report] Order of typesystem loads plays role even if loaded typesystems have `generate="no"`. It's hard to find some principles, but if you get error on shiboken build, bear in mind this.

5.1 [report] if typesystem definition(.xml file) is loaded once with `generate="no"` for example in child definition(another .xml file loaded using `<load-typesystem>`) , shiboken generates no wrapper for it even if it is loaded later with `generate="yes"`.

6. [report] shiboken doesn't take into account namespace of `none` in util.h. Temporary fixed by adding namespace in tools/fix_generated_sources.py.
