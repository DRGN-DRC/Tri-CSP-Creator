from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need fine tuning.

#homeFolder = os.path.abspath(os.path.dirname(sys.argv[0]))
buildOptions = dict(
	packages = [],
	excludes = [],
	include_files=[
	'Changelog.txt',
	'GALE01.ini',
	'GIMP plug-ins',
	'gimprcTCC',
	'GrNLa (FD, stars removed).dat',
	'imgs',
	'IrAls (VS Screen).usd',
	'ReadMe.txt',
	'tkdnd2.7'
	])

#base = 'Win32GUI' if sys.platform=='win32' else None
base = 'Console'

executables = [
	Executable(
		"Tri-CSP Creator.py", 
		icon='TCC_icon (all sizes).ico', # For the executable file icon. "appIcon.png" is for the GUI's window icon.
		base=base)
]

setup(name="Tri-CSP Creator",
	#version = dtwMainScript.programVersion,
	version = '1.1',
	description = 'Creates Character Select Portraits for SSBM.',
	options = dict( build_exe = buildOptions ),
	executables = executables
)
