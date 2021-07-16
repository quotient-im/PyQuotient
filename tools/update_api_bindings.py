import lxml.etree as ET
from pathlib import Path
from typing import List

from file_utils import replace_in_file


def update_typesystem_loads(project_dir: Path):
    typestem_dir = project_dir / 'PyQuotient' / 'typesystems'
    typesystem_csapi_path = typestem_dir / 'typesystem_csapi.xml'

    def format_load(typesystem_file: Path):
        resolved_path = typesystem_file.relative_to(typestem_dir)
        return f'  <load-typesystem name="{resolved_path}" />'
    
    def filter_typesystem(typesystem_file: Path):
        return not str(typesystem_file).startswith(str(typestem_dir / 'csapi' / 'definitions'))

    typesystem_files = filter(filter_typesystem, list((typestem_dir / 'csapi').rglob('*.xml')))
    loads = '\n'.join(map(format_load, typesystem_files))

    replace_in_file(
        typesystem_csapi_path,
        r'<!-- CSAPI -->(.|\n)*<!-- CSAPI end -->',
        '<!-- CSAPI -->\n' + loads + '\n  <!-- CSAPI end -->'
    )


def update_bindings_h(header_files: List[Path], project_dir: Path):
    bindings_h_path = project_dir / 'PyQuotient' / 'bindings.h'

    relative_path = project_dir / 'PyQuotient'
    def format_include(header: Path):
        resolved_path = header.relative_to(relative_path)
        return f'#include "{resolved_path}"'

    includes = '\n'.join(map(format_include, header_files))
    replace_in_file(
        bindings_h_path,
        r'/\* CSAPI \*/(.|\n)*/\* CSAPI end \*/',
        '/* CSAPI */\n' + includes + '\n/* CSAPI end */'
    )


def update_cmake(project_dir):
    cmake_path = project_dir / 'CMakeLists.txt'
    source_files = list((project_dir / 'build' / 'PyQuotient').rglob('*.*'))

    wrappers = map(lambda x: x.name, source_files)
    replace_in_file(
        cmake_path,
        r'# generated wrappers\nset\(generated_wrappers(.|\n)*\)\n# generated wrappers end',
        '# generated wrappers\nset(generated_wrappers\n' + '\n'.join(wrappers) + '\n)\n# generated wrappers end'
    )


def add_data_definition(project_dir: Path):
    # TODO: namespace-type
    typestem_dir = project_dir / 'PyQuotient' / 'typesystems'
    typesystem_files = list((typestem_dir / 'csapi' / 'definitions').rglob('*.xml'))
    typesystem_files += list((typestem_dir / 'application-service' / 'definitions').rglob('*.xml'))

    csapi_definition_filepath = typestem_dir / 'typesystem_csapi.xml'
    csapi_def_tree = ET.parse(str(csapi_definition_filepath))
    csapi_def_root = csapi_def_tree.getroot()

    # collect and remove all existing: non-generated are only <load-typesystem>,
    # all other elements can be removed
    for namespace_type in csapi_def_root.findall('namespace-type'):
        csapi_def_root.remove(namespace_type)

    namespace_type = ET.Element('namespace-type')
    namespace_type.attrib['name'] = 'Quotient'
    csapi_def_root.append(namespace_type)
    for typesystem_file in typesystem_files:
        tree = ET.parse(str(typesystem_file))
        for element in tree.getroot().iter():
            if element.tag == 'value-type':
                namespace_type.append(element)

    csapi_def_tree.write(str(csapi_definition_filepath))


def update():
    file_path = Path(__file__).parent.resolve()
    project_dir = file_path / '..'
    api_dir_path = project_dir / 'PyQuotient' / 'libQuotient' / 'lib' / 'csapi'
    header_files = list(api_dir_path.rglob('*.h'))

    update_typesystem_loads(project_dir)
    update_bindings_h(header_files, project_dir)
    update_cmake(project_dir)
    add_data_definition(project_dir)


if __name__ == '__main__':
    update()
