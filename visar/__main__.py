import visar.cmd
import visar.py
import visar.repl
import visar.vis


def load_modules(_ns: visar.repl.Namespace) -> None:
    import visar.mod
    import visar.vis

    for m in [
        visar.mod.default,
        visar.mod.base,
        visar.mod.c_types,
        visar.mod.size,
        visar.mod.unicode,
        visar.mod.time,
        visar.mod.error,
        visar.mod.num_word,
        visar.mod.pint,
        visar.mod.chemistry,
    ]:
        visar.vis.enable(m)


visar.repl.main(
    [
        visar.cmd.mod_cmd,
        visar.py.mod_expr,
        visar.py.mod_stmt,
    ],
    lambda: input(">>> "),
    load_modules,
)
