import nox
import sys
import os
import shutil
import re

from pathlib import Path

sys.path.append(os.path.dirname(__file__))


def split_cmd(cmd: str):
    return cmd.strip().split(" ")


test_deps = [
    '.',
    'coverage'
]


class Tasks:
    test = lambda posargs='': 'python -m unittest discover'
    test_integration = lambda: "python ./tests/run_tests.py"
    coverage = lambda posargs: f'coverage {posargs}'
    build_wheel = 'python -m setup bdist_wheel'
    send = r'twine upload dist/*.whl'
    docs = 'pdoc --html kalash --force'


@nox.session()
def test(session: nox.Session):
    """Run unit tests under coverage (use `nocov` arg to run without coverage)"""
    session.install(*test_deps)
    if session.posargs:
        if 'nocov' in session.posargs:
            # run tests without coverage:
            session.run('python', '-m', *split_cmd(Tasks.test()), *session.posargs)
            return
    # run tests with coverage:
    session.run(*split_cmd(Tasks.coverage('erase')))
    session.run(
        *split_cmd(Tasks.coverage('run -m unittest discover')),
        *session.posargs
    )


@nox.session()
def cov_report(session: nox.Session):
    """Combine coverage.py files and generate an XML report"""
    session.install(
        'coverage'
    )
    session.run(*split_cmd(Tasks.coverage('xml')), '-i')


def _copy_and_sanitize_paths_for_pdoc3(doc_source_path, target_path):
    if not os.path.exists(target_path):
        shutil.copytree(doc_source_path, target_path)
    else:
        shutil.rmtree(target_path)
        shutil.copytree(doc_source_path, target_path)
    
    for root, dirs, files in os.walk(target_path):
        for file in files:
            if file.endswith('.md'):
                file_full_path = str(Path(root) / file)
                with open(file_full_path, 'r') as f:
                    text = f.read()
                # match [blah](blah.md#blah-blah-blah)
                pattern = r'(\[.+?\]\()(.+?)(\.md)(\#.+?\))'
                replacement_text = re.sub(pattern, r'\g<1>\g<4>', text)
                with open(file_full_path, 'w') as f:
                    f.write(replacement_text)


@nox.session()
def docs(session: nox.Session):
    """Build HTML documentation."""
    built_docs_dir = 'kalash/built_docs'
    pdoc_dir = 'kalash/pdoc'
    res_dir = 'kalash/res'
    target_res = Path(built_docs_dir) / 'html' / 'res'
    if not os.path.exists(built_docs_dir):
        os.makedirs(built_docs_dir)
    _copy_and_sanitize_paths_for_pdoc3('kalash/doc', pdoc_dir)
    session.install('pdoc3', '.')
    cwd = os.getcwd()
    session.chdir(built_docs_dir)
    session.run(*split_cmd(Tasks.docs))
    session.chdir(cwd)
    if os.path.exists(target_res):
        shutil.rmtree(target_res)
    shutil.copytree(res_dir, target_res)


@nox.session()
def whl(session: nox.Session):
    """Build wheel (remember to build docs first)"""
    session.install(
        'wheel',
        'setuptools',
        '.'
    )
    session.run(*split_cmd(Tasks.build_wheel))


@nox.session()
def send(session: nox.Session):
    """Send wheels from the `dist` folder to Technica Nexus"""
    session.install(
        'twine'
    )
    session.run(*split_cmd(Tasks.send))


@nox.session()
def clean(session: nox.Session):
    """Remove potentially lingering files"""
    to_delete = [
        ".coverage",
        "kalash_reports"
    ]
    for p in to_delete:
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
