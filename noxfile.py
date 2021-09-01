import nox
import sys, os

sys.path.append(os.path.dirname(__file__))


def split_cmd(cmd: str):
    return cmd.strip().split(" ")


test_deps = [
    '.',
    'coverage'
]


class Tasks:
    test = lambda posargs='': f'python -m unittest discover'
    test_integration = lambda: "python ./tests/run_tests.py"
    coverage = lambda posargs: f'coverage {posargs}'
    build_wheel = 'python -m setup bdist_wheel'
    send = r'twine upload dist/*.whl'


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
