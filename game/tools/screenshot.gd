# Снимок экрана игры для проверки композиции без ручного запуска.
# Запуск (с окном, без --headless, иначе рендера нет):
#   "$GODOT" --path game -s res://tools/screenshot.gd -- <секунды> <путь.png>
# По умолчанию 3 секунды и docs/playtests/shot.png относительно корня репозитория.
extends SceneTree

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	var delay := 3.0
	var out := "res://../docs/playtests/shot.png"
	if args.size() >= 1:
		delay = float(args[0])
	if args.size() >= 2:
		out = args[1]
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	root.add_child(main)
	await create_timer(delay).timeout
	var img := root.get_viewport().get_texture().get_image()
	var err := img.save_png(out)
	print("screenshot: ", out, " size=", img.get_size(), " err=", err)
	quit()
