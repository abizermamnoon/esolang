import readline
import esolang.level0_arithmetic
import esolang.level1_statements
import esolang.level2_loops
import esolang.level3_functions


def run_repl(lang = esolang.level3_functions):
    parser = lang.parser
    interpreter = lang.Interpreter()
    while True:
        try:
            cmd = input('esolang> ')
            tree = parser.parse(cmd)
            result = interpreter.visit(tree)
            if result is not None:
                print(result)
        except EOFError:
            break
        except Exception as e:
            print(e)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--level', default=3, type=int)
    args = parser.parse_args()

    run_repl()
