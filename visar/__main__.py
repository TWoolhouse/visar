import visar.cmd
import visar.mod
import visar.py
import visar.repl
import visar.vis

visar.vis.enable(
    visar.mod.default,
    visar.mod.base,
    visar.mod.c_types,
    visar.mod.size,
    visar.mod.unicode,
    visar.mod.time,
    visar.mod.error,
    visar.mod.num_word,
)


visar.repl.main(
    [
        visar.cmd.mod_cmd,
        visar.py.mod_expr,
        visar.py.mod_stmt,
    ],
    lambda: input(">>> "),
)
