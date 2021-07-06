from pathlib import Path

from file_utils import replace_in_file


def fix():
    file_path = Path(__file__).parent
    project_path = file_path / '..'
    generated_files_path = project_path / 'build' / 'PyQuotient'

    original_part = '#include <pyquotient_python.h>'
    replace_in_file(
        generated_files_path / 'pyquotient_python.h',
        original_part,
        '',
        use_re=False
    )

    original_part = 'PyTypeObject **SbkPyQuotientTypes;\nSbkConverter **SbkPyQuotientTypeConverters;'
    replace_in_file(
        generated_files_path / 'pyquotient_module_wrapper.cpp',
        original_part,
        '',
        use_re=False
    )
    print("Fixed generated source files")


if __name__ == '__main__':
    fix()
