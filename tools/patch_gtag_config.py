from pathlib import Path
from shutil import copyfile

from file_utils import replace_in_file


def copy_and_patch():
    file_path = Path(__file__).parent
    project_path = file_path / '..'
    gtag_original_config_path = project_path / 'PyQuotient' / 'libQuotient' / 'gtad' / 'gtad.yaml'
    gtag_config_path = project_path / 'gtad' / 'gtad.yaml'

    copyfile(gtag_original_config_path, gtag_config_path)

    # operation template
    original_config_part = '\.h: "{{>operation\.h\.mustache}}"\n *\.cpp: "{{>operation\.cpp\.mustache}}"'
    replace_in_file(
        gtag_config_path,
        original_config_part,
        '.xml: "{{>../../../gtad/typesystem.xml.mustache}}"\n\n'
    )

    # data template
    original_config_part = '\.h: "{{>data\.h\.mustache}}"'
    replace_in_file(
        gtag_config_path,
        original_config_part,
        '.xml: "{{>../../../gtad/typesystem_data.xml.mustache}}"\n\n'
    )

    # remove unneeded includes
    original_config_part = ' *imports: \'?"events/eventloader\.h"\'? *'
    replace_in_file(
        gtag_config_path,
        original_config_part,
        '',
    )

    original_config_part = ' *imports: \'?"events/roommemberevent\.h"\'? *'
    replace_in_file(
        gtag_config_path,
        original_config_part,
        '',
    )

    original_config_part = '        imports: <QtCore/QIODevice>\n'
    replace_in_file(
        gtag_config_path,
        original_config_part,
        '',
        use_re=False
    )


if __name__ == '__main__':
    copy_and_patch()
