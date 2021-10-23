 #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# This file's encoding: UTF-8

# Written in Python v2.7.9-12 by DRGN of SmashBoards (Daniel R. Cappel).

programVersion = '1.1'

# For main logic
import os, sys
import time, math
import argparse, subprocess
from collections import OrderedDict
import webbrowser 		# For creating a link to go to the official thread

# For GUI elements
import ttk, tkFont
from newTkDnD import TkDND 			# Access files given (drag-and-dropped) onto the running program GUI.
from PIL import Image, ImageTk 		# Just needed for the app icon
import tkMessageBox, tkFileDialog
from Tkinter import Tk, Text, StringVar, BooleanVar, PhotoImage


class triCspCreator( object ):

	def __init__( self, parent, dnd ):
		style = ttk.Style()
		style.configure( 'newFrame.TFrame', background='#e9e9ff' )
		style.configure( 'newLabel.TLabel', background='#e9e9ff' )
		style.configure( 'newCheckbox.TCheckbutton', background='#e9e9ff' )
		style.configure( 'largeBttn.TButton', font=("Helvetica", 11, "bold italic") ) # Used for the "Create CSP" button
		linkFont = tkFont.Font( family="Helvetica", size=10, underline=True )
		style.configure( 'linkLabel.TLabel', font=linkFont, background='#e9e9ff', foreground='#00f' )

		self.rootFrame = ttk.Frame( parent, style='newFrame.TFrame' )
		self.parent = parent
		self.pathsInputWidth = 30
		self.maxLines = 10
		self.animationSpeed = .002
		self.firstTimeMoving = True
		self.creationInProgress = False

		self.mainFrame = mainFrame = ttk.Frame( self.rootFrame, style='newFrame.TFrame' )

		# Add the top labels
		ttk.Label( mainFrame, text='Left Image(s)', style='newLabel.TLabel' ).grid( row=0, column=1 )
		ttk.Label( mainFrame, text='Center Image(s)', style='newLabel.TLabel' ).grid( row=0, column=2 )
		ttk.Label( mainFrame, text='Right Image(s)', style='newLabel.TLabel' ).grid( row=0, column=3 )

		# Placeholder labels (preserves space along the sides of the Text widgets for later addition of line labels)
		ttk.Label(mainFrame, text='', style='newLabel.TLabel', width=3 ).grid( row=0, column=0, padx=6 )
		ttk.Label(mainFrame, text='', style='newLabel.TLabel', width=3 ).grid( row=0, column=4, padx=6 )

		# Input fields for the left, center, and right CSP images
		self.leftPathsInput = Text( mainFrame, width=self.pathsInputWidth, height=self.maxLines, 
			highlightbackground='#b7becc', highlightcolor='#0099f0', highlightthickness=2, borderwidth=0, wrap='none' )
		self.centerPathsInput = Text( mainFrame, width=self.pathsInputWidth, height=self.maxLines, 
			highlightbackground='#b7becc', highlightcolor='#0099f0', highlightthickness=2, borderwidth=0, wrap='none' )
		self.rightPathsInput = Text( mainFrame, width=self.pathsInputWidth, height=self.maxLines, 
			highlightbackground='#b7becc', highlightcolor='#0099f0', highlightthickness=2, borderwidth=0, wrap='none' )
		self.leftPathsInput.grid( row=1, column=1 )
		self.centerPathsInput.grid( row=1, column=2 )
		self.rightPathsInput.grid( row=1, column=3 )

		for widget in mainFrame.winfo_children():
			widget.grid_configure( padx=4, pady=4 )
			widget.grid_propagate( False )

		# Add drag-and-drop event handlers for file input
		dnd.bindtarget( self.leftPathsInput, self.dndHandler, 'text/uri-list' )
		dnd.bindtarget( self.centerPathsInput, self.dndHandler, 'text/uri-list' )
		dnd.bindtarget( self.rightPathsInput, self.dndHandler, 'text/uri-list' )

		# Add focus event handlers (for changing width of text widgets)
		self.leftPathsInput.bind( '<FocusIn>', self.resizeTextFields )
		self.centerPathsInput.bind( '<FocusIn>', self.resizeTextFields )
		self.rightPathsInput.bind( '<FocusIn>', self.resizeTextFields )

		mainFrame.pack()

		self.subFrame = subFrame = ttk.Frame( self.rootFrame, style='newFrame.TFrame' )

		# Mask file input
		self.maskRow = ttk.Frame( subFrame, padding=15, style='newFrame.TFrame' )
		ttk.Label( self.maskRow, text='Mask (optional):', style='newLabel.TLabel', width=17, anchor='n' ).pack( side='left' )
		self.maskFile = StringVar()
		self.maskFileEntry = ttk.Entry( self.maskRow, textvariable=self.maskFile, width=83 )
		self.maskFileEntry.pack( side='left', expand=True, padx=8 )
		self.maskFileEntry.bind( '<KeyRelease>', self.validatePath )
		ttk.Button( self.maskRow, text='Choose', command=self.loadMask ).pack( side='left', padx=3 )
		maskImage = PhotoImage( file='imgs/mask.gif' )
		self.maskIconWidget = ttk.Label( self.maskRow, image=maskImage, style='newLabel.TLabel', cursor='hand2' )
		self.maskIconWidget.image = maskImage # Keeps a reference to the image to prevent garbage collection
		self.maskIconWidget.pack( side='left', padx=5 )
		self.maskIconWidget.bind( '<1>', self.openDir )
		self.maskRow.pack( fill='x', expand=True )
		dnd.bindtarget( self.maskRow, self.dndHandler, 'text/uri-list' )

		# Configuration file input
		self.configRow = ttk.Frame( subFrame, padding=15, style='newFrame.TFrame' )
		ttk.Label( self.configRow, text='Config File:', style='newLabel.TLabel', width=17, anchor='n' ).pack( side='left' )
		self.configFile = StringVar()
		self.configFileEntry = ttk.Entry( self.configRow, textvariable=self.configFile, width=83 )
		self.configFileEntry.pack( side='left', expand=True, padx=8 )
		self.configFileEntry.bind( '<KeyRelease>', self.validatePath )
		ttk.Button( self.configRow, text='Choose', command=self.loadConfig ).pack( side='left', padx=3 )
		fileIconImage = PhotoImage( file='imgs/fileIcon.gif' )
		self.fileIconWidget = ttk.Label( self.configRow, image=fileIconImage, style='newLabel.TLabel', cursor='hand2' )
		self.fileIconWidget.image = fileIconImage # Keeps a reference to the image to prevent garbage collection
		self.fileIconWidget.pack( side='left', padx=5 )
		self.fileIconWidget.bind( '<1>', self.openInDefaultProgram )
		self.configRow.pack( fill='x', expand=True )
		dnd.bindtarget( self.configRow, self.dndHandler, 'text/uri-list' )

		# Output folder path
		self.outputPathRow = ttk.Frame( subFrame, padding=15, style='newFrame.TFrame' )
		ttk.Label( self.outputPathRow, text='Output Folder:', style='newLabel.TLabel', width=17, anchor='n' ).pack( side='left' )
		self.outputPath = StringVar()
		self.outputPathEntry = ttk.Entry( self.outputPathRow, textvariable=self.outputPath, width=83 )
		self.outputPathEntry.pack( side='left', expand=True, padx=8 )
		self.outputPathEntry.bind( '<KeyRelease>', self.validatePath )
		ttk.Button( self.outputPathRow, text='Choose', command=self.loadOutputPath ).pack( side='left', padx=3 )
		folderIconImage = PhotoImage( file='imgs/folderIcon.gif' )
		self.folderIconWidget = ttk.Label( self.outputPathRow, image=folderIconImage, style='newLabel.TLabel', cursor='hand2' )
		self.folderIconWidget.image = folderIconImage # Keeps a reference to the image to prevent garbage collection
		self.folderIconWidget.pack( side='left', padx=5 )
		self.folderIconWidget.bind( '<1>', self.openDir )
		self.outputPathRow.pack( fill='x', expand=True )
		dnd.bindtarget( self.outputPathRow, self.dndHandler, 'text/uri-list' )

		# Final buttons row
		self.buttonsRow = ttk.Frame( subFrame, padding="0 10 0 30", style='newFrame.TFrame' )
		self.createButton = ttk.Button( self.buttonsRow, text='  Create CSP  ', command=self.createCSP, style='largeBttn.TButton' )
		self.createButton.grid( row=0, column=0, padx=0, ipadx=3, ipady=3, sticky='w' )
		ttk.Button( self.buttonsRow, text='Clear', command=self.clearTexts ).grid( row=0, column=1, padx=60, pady=8 )
		self.saveHighRes = BooleanVar()
		ttk.Checkbutton( self.buttonsRow, text='  Create in\n  High-Res', variable=self.saveHighRes, style='newCheckbox.TCheckbutton' ).grid( row=1, column=0, ipadx=15, sticky='w' )
		def gotoOfficialThread( event ): webbrowser.open( 'https://smashboards.com/threads/tri-csp-creator.448104/unread' )
		helpLabel = ttk.Label( self.buttonsRow, text='Halp!\n(Open official thread)', style='linkLabel.TLabel', cursor='hand2', justify='center' )
		helpLabel.grid( row=1, column=1 )
		helpLabel.bind( '<1>', gotoOfficialThread )

		self.programStatus = StringVar()
		self.programStatus.set( 'Ready!' )
		ttk.Label( self.buttonsRow, textvariable=self.programStatus, style='newLabel.TLabel', width=22, anchor='n' ).grid( row=0, column=3, rowspan=2 ) #, columnspan=2
		self.buttonsRow.pack()

		subFrame.pack( fill='x', expand=True )

		self.rootFrame.pack()

		# Add key bindings for "Select All (CTRL-A)"
		self.rootFrame.bind_class( "Text", "<Control-a>", self.selectAll )
		self.rootFrame.bind_class( "TEntry", "<Control-a>", self.selectAll )

	def resizeTextFields( self, event ): # Adjust size of the text widget in focus to occupy most of the space
		widgetsToResize = ( self.leftPathsInput, self.centerPathsInput, self.rightPathsInput )
		focusedTextWidget = event.widget

		while focusedTextWidget['width'] < self.pathsInputWidth * 2 and self.mainFrame.focus_get() == focusedTextWidget: # Second argument causes loop to end if another Text gains focus
			for inputField in widgetsToResize:
				isFocusedWidget = ( inputField == focusedTextWidget )

				currentWidth = inputField['width']

				if isFocusedWidget:
					targetWidth = self.pathsInputWidth * 2
					stepDistance = int( math.ceil( ( targetWidth - currentWidth ) / 30.0 ) )
				else:
					targetWidth = self.pathsInputWidth / 2
					stepDistance = int( math.floor( ( targetWidth - currentWidth ) / 30.0 ) )

				if stepDistance != 0:
					totalDistanceToMove = abs( targetWidth - currentWidth )

					if totalDistanceToMove > -2 and totalDistanceToMove < 2: inputField['width'] = targetWidth
					elif self.firstTimeMoving and stepDistance > 0:
						inputField['width'] = inputField['width'] + ( stepDistance * 2 )
					else:
						inputField['width'] = inputField['width'] + stepDistance

			self.mainFrame.update()

		if self.firstTimeMoving: self.firstTimeMoving = False

	def dndHandler( self, event ):
		# The paths that this event recieves are in one string, each enclosed in {} brackets (if they contain a space) and separated by a space. Turn this into a list.
		paths = event.data.replace('{', '').replace('}', '')
		drive = paths[:2]

		filepaths = [drive + path.strip() for path in paths.split(drive) if path != '']

		#self.parent.deiconify() # Brings the program to the front (application z-order).
		self.fileHandler( event, filepaths )

	def fileHandler( self, event, filepaths ):
		focusedWidget = event.widget

		if focusedWidget == self.maskRow:
			if len( filepaths ) > 1: tkMessageBox.showinfo( message='Please choose only one image to use as a mask for the left and right images.', title='Invalid Input' )
			elif len( filepaths ) == 1: self.loadMask( filepaths[0] )

		elif focusedWidget == self.configRow:
			if len( filepaths ) > 1: tkMessageBox.showinfo( message='You may only open one config file at a time.', title='Invalid Input' )
			elif len( filepaths ) == 1: self.loadConfig( filepaths[0] )

		elif focusedWidget == self.outputPathRow:
			if len( filepaths ) > 1: tkMessageBox.showinfo( message='Please choose only one folder for an output path.', title='Invalid Input' )
			elif not os.path.isdir( filepaths[0] ): tkMessageBox.showinfo( message='The output path must be a folder.', title='Invalid Input' )
			elif '&' in filepaths[0]: tkMessageBox.showinfo( message='GIMP through command line cannot handle paths with ampersands (&). Please modify the path and try again.', title='Invalid Input' )
			elif len( filepaths ) == 1: self.loadOutputPath( filepaths[0] )

		else: # Should be an input field for left, center, or right screenshot images
			# Remove existing line labels along the left & right headers
			self.clearLineNumberLabels()

			# Add the path(s) to the Text widget they're being dragged to
			notAdded = []
			for path in filepaths:
				if '&' in path: notAdded.append( path )
				else:
					focusedWidget.insert( 'end', '"' + path + '"\n' ) # Double quotes added just for aesthetics (easier on the eye to identify end of string)
			if notAdded:
				tkMessageBox.showinfo( message='GIMP through command line cannot handle paths with ampersands (&). These paths could not be added:\n\n' + '\n'.join(notAdded), title='Invalid Input' )

			# Try to set the config path if it's not already set and this is the center image input field
			if focusedWidget == self.centerPathsInput and not self.configFile.get().replace( '"', '' ).strip():
				configFile = ''
				for path in filepaths:
					parentFolder = os.path.dirname( path )
					if '&' not in parentFolder:
						# Look for a config file
						for item in os.listdir( parentFolder ):
							if item.endswith( '.txt' ) and 'config' in item:
								configFile = item
								break
						break
				if configFile:
					self.loadConfig( os.path.join(parentFolder, item) )

			# Get the max number of paths among all Text input fields
			mostPaths = 0
			for widget in ( self.leftPathsInput, self.centerPathsInput, self.rightPathsInput ):
				pathsInInputField = len( self.recallFilepaths(widget) )
				if pathsInInputField > mostPaths: mostPaths = pathsInInputField

			if mostPaths > self.maxLines: mostPaths = self.maxLines

			if mostPaths > 0: # Add new line number labels
				lineNumbering = '\n'.join( [str(number) for number in range( 1, mostPaths+1 )] )
				ttk.Label( self.mainFrame, text=lineNumbering, style='newLabel.TLabel' ).grid( row=1, column=0, sticky='n', ipady=6, padx=6 )
				ttk.Label( self.mainFrame, text=lineNumbering, style='newLabel.TLabel' ).grid( row=1, column=4, sticky='n', ipady=6, padx=6 )

			# Modify the Create CSP button text for plurality (the detail! omg)
			if mostPaths > 1:
				self.createButton['text'] = '  Create CSPs  '
			else:
				self.createButton['text'] = '  Create CSP  '

	def loadMask( self, filepath='' ):
		if not filepath: # No files given; prompt to choose a file.
			filepath = tkFileDialog.askopenfilename(
				title="Choose an image to use as a mask for cutting out the left and right images.", 
				#initialdir=settings.get( 'General Settings', 'defaultSearchDirectory' ),
				filetypes=[('Image file', '*.png'), ('All files', '*.*')]
				)

		if filepath:
			if '&' in filepath:
				tkMessageBox.showinfo( message='GIMP through command line cannot handle paths with ampersands (&). Please modify the path and try again.', title='Invalid Input' )
				self.maskFile.set( '' )
			else:
				self.maskFile.set( filepath ) # Sets the stringVar used by the GUI's Entry widget

		# Activate/deactivate the associated image
		self.validatePath( '', widget=self.maskFileEntry )

	def loadConfig( self, filepath='' ):
		if not filepath: # No files given; prompt to choose a file.
			filepath = tkFileDialog.askopenfilename(
				title="Choose a config file to open.", 
				#initialdir=settings.get( 'General Settings', 'defaultSearchDirectory' ),
				filetypes=[('Text file', '*.txt'), ('All files', '*.*')]
				)

		if filepath:
			if '&' in filepath:
				tkMessageBox.showinfo( message='GIMP through command line cannot handle paths with ampersands (&). Please modify the path and try again.', title='Invalid Input' )
				self.configFile.set( '' )
			else:
				self.configFile.set( filepath ) # Sets the stringVar used by the GUI's Entry widget

		# Activate/deactivate the associated image
		self.validatePath( '', widget=self.configFileEntry )

	def loadOutputPath( self, outPath='' ):
		outPath = tkFileDialog.askdirectory(
				title='Where would you like to save these files?',
				#initialdir=settings.get( 'General Settings', 'defaultSearchDirectory' ),
				#parent=root,
				mustexist=True )

		if outPath and os.path.isdir( outPath ): self.outputPath.set( outPath )

		# Activate/deactivate the associated image
		self.validatePath( '', widget=self.outputPathEntry )

	def validatePath( self, event, widget=None ): # Ensures valid paths exist for the mask and config files, and highlights their icon image if they do.
		if event: widget = event.widget

		if widget == self.maskFileEntry:
			currentPath = self.maskFile.get().replace( "", '' )
			if currentPath and os.path.exists( currentPath ):
				maskImage = PhotoImage( file='imgs/mask_active.gif' )
			else:
				maskImage = PhotoImage( file='imgs/mask.gif' )

			self.maskIconWidget.configure( image=maskImage )
			self.maskIconWidget.image = maskImage

		elif widget == self.configFileEntry:
			currentPath = self.configFile.get().replace( "", '' )
			if currentPath and os.path.exists( currentPath ):
				fileIconImage = PhotoImage( file='imgs/fileIcon_active.gif' )
			else:
				fileIconImage = PhotoImage( file='imgs/fileIcon.gif' )

			self.fileIconWidget.configure( image=fileIconImage )
			self.fileIconWidget.image = fileIconImage

		elif widget == self.outputPathEntry:
			currentPath = self.outputPath.get().replace( "", '' )
			if currentPath and os.path.isdir( currentPath ):
				folderIconImage = PhotoImage( file='imgs/folderIcon_active.gif' )
			else:
				folderIconImage = PhotoImage( file='imgs/folderIcon.gif' )

			self.folderIconWidget.configure( image=folderIconImage )
			self.folderIconWidget.image = folderIconImage

	def openDir( self, event ): # Used for opening directories for the mask and output folders
		#textField = event.widget.master.winfo_children()[1]
		dirPath = ''
		if event.widget == self.maskIconWidget:
			dirPath = os.path.dirname( self.maskFile.get().replace( '"', '' ) )
		else:
			dirPath = self.outputPath.get().replace( '"', '' )

		dirPath = os.path.normpath( dirPath )

		if os.path.isdir( dirPath ):
			command = '"%SystemRoot%\\explorer.exe" "' + dirPath + '"'
			try:
				outputStream = subprocess.check_output( command, shell=True, stderr=subprocess.STDOUT, creationflags=0x08000000 )
			except subprocess.CalledProcessError as error:
				outputStream = str( error.output )
				if len( outputStream ) != 0:
					exitCode = str( error.returncode )
					tkMessageBox.showinfo( 'Directory Not Found', 'IPC error: \n\n' + outputStream + '\n\nErrorlevel ' + exitCode )
		elif dirPath != '': tkMessageBox.showinfo( 'Directory Not Found', 'Could not find the following directory: \n\n' + dirPath )

	def openInDefaultProgram( self, event ): # Opens a file (the loaded config file in this case) in the systems default program for that filetype
		filepath = self.configFile.get().replace("", '')

		if os.path.exists( filepath ):
			if sys.platform.startswith( 'darwin' ): subprocess.call( ('open', filepath) )
			elif os.name == 'nt': os.startfile( filepath )
			elif os.name == 'posix': subprocess.call( ('xdg-open', filepath) )

	def recallFilepaths( self, widget ):
		filepaths = []
		for i in xrange( int(widget.index('end-1c').split('.')[0]) ):
			line = widget.get(str(i+1)+'.0', str(i+2)+'.0-1c').replace( '"', '' )
			if line != '': filepaths.append( line )
		return filepaths

	def createCSP( self ):
		# Check that processing isn't already in-progress
		if not self.creationInProgress:

			# Some last-minute validation on the config file
			configPath = self.configFile.get().replace( '"', '' )
			if not configPath:
				tkMessageBox.showinfo( message='No config file has been chosen!', title='Invalid Input' )
			elif not os.path.exists( configPath ):
				tkMessageBox.showinfo( message='The config file could not be found (make sure that it has not been moved/renamed/deleted).', title='Invalid Input' )
			elif not configPath.lower().endswith( '.txt' ):
				tkMessageBox.showinfo( message='The given config file does not appear to be a text file (.txt)!', title='Invalid Input' )

			else:
				self.creationInProgress = True
				self.createButton['state'] = 'disabled'
				self.createButton.update()
				time.sleep( .2 )

				try:
					# Collect the inputs from the various text fields
					leftImagePaths = self.recallFilepaths( self.leftPathsInput )
					centerImagePaths = self.recallFilepaths( self.centerPathsInput )
					rightImagePaths = self.recallFilepaths( self.rightPathsInput )

					configuration = parseConfigurationFile( configPath )
					maskPath = self.maskFile.get().replace( '"', '' )
					outPath = self.outputPath.get().replace( '"', '' )

					# Make sure there's at least one image set available to be processed
					if len( leftImagePaths ) == 0 or len( centerImagePaths ) == 0 or len( rightImagePaths ) == 0:
						tkMessageBox.showinfo( message='To create at least one complete CSP, you must provide a left, center, and right image.', title='Invalid Input' )
						return

					# Prepare the given input, and process it with GIMP
					extraImages, skippedSets = self.beginGimpAutomation( leftImagePaths, centerImagePaths, rightImagePaths, maskPath, '', outPath, configuration, self.saveHighRes.get() )

					# Provide warnings to the user for any images not processed
					if extraImages:
						tkMessageBox.showinfo( 'The following images were not processed because no complete set was given for them:\n\n' + '\n'.join(extraImages) )
					if skippedSets:
						tkMessageBox.showinfo( 'Image set ' + grammarfyList( skippedSets ) + ' could not be processed because one of the images in the set could not be found.' )

					self.creationInProgress = False
					self.createButton['state'] = 'normal'
					self.programStatus.set( 'Processing complete' )
					print '\nProcessing complete.'
					
				except Exception as e:
					self.creationInProgress = False
					self.createButton['state'] = 'normal'
					self.programStatus.set( 'Processing failed' )
					print e

		#else:
			#print 'processing already in-progress'

	def selectAll( self, event ): # Adds bindings for normal CTRL-A functionality.
		if event.widget.winfo_class() == 'Text': event.widget.tag_add( 'sel', '1.0', 'end' )
		elif event.widget.winfo_class() == 'TEntry': event.widget.selection_range( 0, 'end' )

	def clearLineNumberLabels( self ):
		# Remove existing line labels along the left & right headers
		for widget in self.mainFrame.winfo_children():
			gridInfo = widget.grid_info()
			if ( gridInfo['column'] == '0' or gridInfo['column'] == '4' ) and gridInfo['row'] != '0': widget.destroy()

	def clearTexts( self ):
		# Remove the line number labels
		self.clearLineNumberLabels()

		# Clear all text entires besides the output path.
		self.leftPathsInput.delete( '1.0', 'end' )
		self.centerPathsInput.delete( '1.0', 'end' )
		self.rightPathsInput.delete( '1.0', 'end' )
		self.configFile.set( '' )
		self.maskFile.set( '' )

		# Reset the mask & config file loaded icons
		self.validatePath( '', widget=self.maskFileEntry )
		self.validatePath( '', widget=self.configFileEntry )

		# Reset text of Create button (may have plural 's' added)
		self.createButton['text'] = '  Create CSP  '

	def beginGimpAutomation( self, leftImagePaths, centerImagePaths, rightImagePaths, maskImagePath, configFilePath, outputPath, configuration, saveHighRes ):
		#gimpExeFolder, gimpExeName = determineExePath()
		if not gimpExeFolder: return

		# Get the length of the shortest list, this will be how many CSPs will be created
		cspsToCreate = 0
		for pathsList in ( leftImagePaths, centerImagePaths, rightImagePaths ):
			totalImages = len( pathsList )

			if cspsToCreate == 0 or totalImages < cspsToCreate: cspsToCreate = totalImages

		print '\nTotal CSPs to create:', cspsToCreate

		# Separate out the "extra" images that will not be processed
		extraImages = []
		leftImagePaths = leftImagePaths[:cspsToCreate]
		centerImagePaths = centerImagePaths[:cspsToCreate]
		rightImagePaths = rightImagePaths[:cspsToCreate]
		extraImages.extend( leftImagePaths[cspsToCreate:] )
		extraImages.extend( centerImagePaths[cspsToCreate:] )
		extraImages.extend( rightImagePaths[cspsToCreate:] )

		# Format the file paths in a way that GIMP understands
		maskImagePath = preparePathForGimpCmd( maskImagePath )
		configFilePath = preparePathForGimpCmd( configFilePath )
		outputPath = preparePathForGimpCmd( outputPath )

		skippedSets = []
		for i in range( cspsToCreate ):

			if not os.path.exists( leftImagePaths[i] ) or not os.path.exists( centerImagePaths[i] ) or not os.path.exists( rightImagePaths[i] ):
				skippedSets.append( str(i+1) )
				continue

			self.programStatus.set( 'Processing set ' + str(i+1) + ' of ' + str(cspsToCreate) )
			self.buttonsRow.update()

			leftImagePath = preparePathForGimpCmd( leftImagePaths[i] )
			centerImagePath = preparePathForGimpCmd( centerImagePaths[i] )
			rightImagePath = preparePathForGimpCmd( rightImagePaths[i] )

			returnCode, outputStream = callGimpAutomation( gimpExeFolder, gimpExeName, leftImagePath, centerImagePath, rightImagePath, maskImagePath, configFilePath, outputPath, configuration, saveHighRes )
			
			if returnCode == 0:
				print '\nFinished processing group ' + str(i+1) + '.', outputStream
			else:
				print '\nUnable to process group ' + str(i+1) + ';', outputStream
				print 'Return code: ', returnCode

		return extraImages, skippedSets

	# - End of triCspCreator Class -


def initializeGui():
	root = Tk()
	dnd = TkDND( root )
	appIcon = ImageTk.PhotoImage( Image.open('imgs/appIcon.png') )
	root.tk.call( 'wm', 'iconphoto', root._w, appIcon )
	root.title( 'Tri-CSP Creator - v' + programVersion )
	root.resizable( width=False, height=False )

	triCspCreator( root, dnd )

	root.mainloop()


def grammarfyList( theList ): # For example, the list [apple, pear, banana, melon] becomes the string 'apple, pear, banana, and melon'.
	if len(theList) == 1: return str(theList[0])
	elif len(theList) == 2: return str(theList[0]) + ' and ' + str(theList[1])
	else:
		string = ', '.join( theList )
		indexOfLastComma = string.rfind(',')
		return string[:indexOfLastComma] + ', and ' + string[indexOfLastComma + 2:]


def parseArguments():
	# Parse command line arguments
	parser = argparse.ArgumentParser( description='Program to create custom CSPs for SSBM: 20XXHP.' ) # , add_help=False
	subparsers = parser.add_subparsers( title='Run modes', dest='mode',
										description='You can use this program in one of three ways, via ' \
													'"Tri-CSP-Creator.exe gui ...", ' \
													'"Tri-CSP-Creator.exe cmd ...", or ' \
													'"Tri-CSP-Creator.exe cmd-config ..."' )

	interfaceModeParser = subparsers.add_parser( 'gui', 
		help='Run this program using a GUI, which can accept optional arguments for image filepaths to pre-populate those inputs.' )
	interfaceModeParser.add_argument( '-l', '-leftImagePaths', nargs='*', default=[], help='File paths for the left image.' )
	interfaceModeParser.add_argument( '-c', '-centerImagePaths', nargs='*', default=[], help='File paths for the center image.' )
	interfaceModeParser.add_argument( '-r', '-rightImagePaths', nargs='*', default=[], help='File paths for the right image.' )
	interfaceModeParser.add_argument( '-m', '--maskImagePath', default='', help='Use a different layer for use in removing the background.' )

	cmdModeParser = subparsers.add_parser( 'cmd',
		help='Run this program via command line only, in which case image paths and most other arguments are required. Run "Tri-CSP-Creator.exe cmd -h" to see a list of all arguments.' )
	cmdModeParser.add_argument( '-l', '--leftImagePaths', required=True, nargs='+', help='File paths for the left image.' )
	cmdModeParser.add_argument( '-c', '--centerImagePaths', required=True, nargs='+', help='File paths for the center image.' )
	cmdModeParser.add_argument( '-r', '--rightImagePaths', required=True, nargs='+', help='File paths for the right image.' )
	cmdModeParser.add_argument( '-t', '--threshold', required=True, default=50, help="Selection threshold for identifying a screenshot's magenta background." )
	cmdModeParser.add_argument( '-re', '--reverseSides', default=False, help='Horizontally flip the side images.' )
	cmdModeParser.add_argument( '-cx', '--centerImageXOffset', required=True, default=0, help="X coordinate of the center image." )
	cmdModeParser.add_argument( '-cy', '--centerImageYOffset', required=True, default=0, help="Y coordinate of the center image." )
	cmdModeParser.add_argument( '-cs', '--centerImageScaling', required=True, default=1.0, help="Scale of the center image (a float)." )
	cmdModeParser.add_argument( '-sx', '--sideImagesXOffset', required=True, default=0, help="X offset, relative to the side of the CSP, for both side images." )
	cmdModeParser.add_argument( '-sy', '--sideImagesYOffset', required=True, default=0, help="Y offset, relative to the top of the CSP, for both side images." )
	cmdModeParser.add_argument( '-ss', '--sideImagesScaling', required=True, default=1.0, help="Scale of both side images (a float)." )
	cmdModeParser.add_argument( '-shr', '--saveHighRes', action='store_true', help="If true, this will create a large, high-res version of the CSP, instead of the vanilla 136x188. This can't be imported into a disc though." )
	cmdModeParser.add_argument( '-m', '--maskImagePath', default='', help='Use a different layer for use in removing the background.' )
	cmdModeParser.add_argument( '-o', '--outputPath', default='', help='Specify the output folder for saving completed CSPs.' )

	cmdConfigModeParser = subparsers.add_parser( 'cmd-config',
		help='Run this program via command line only, using image filepaths and one configuration filepath as arguments.' )
	cmdConfigModeParser.add_argument( '-l', '--leftImagePaths', required=True, nargs='+', help='File paths for the left image.' )
	cmdConfigModeParser.add_argument( '-c', '--centerImagePaths', required=True, nargs='+', help='File paths for the center image.' )
	cmdConfigModeParser.add_argument( '-r', '--rightImagePaths', required=True, nargs='+', help='File paths for the right image.' )
	cmdConfigModeParser.add_argument( '-f', '--configFile', required=True, help='File paths to a config file containing the necessary arguments.' )
	cmdConfigModeParser.add_argument( '-shr', '--saveHighRes', action='store_true', help="If true, this will create a large, high-res version of the CSP, instead of the vanilla 136x188. This can't be imported into a disc though." )
	cmdConfigModeParser.add_argument( '-m', '--maskImagePath', default='', help='Use a different layer for use in removing the background.' )
	cmdConfigModeParser.add_argument( '-o', '--outputPath', default='', help='Specify the output folder for saving completed CSPs.' )

	return parser.parse_args()


def stringToBool( string ): # Accepts True, true, t, or 1 as "True", and evaluates anything else to "False"
	string = string.strip()[0:1].lower()
	if string == 't' or string == '1': return True
	else: return False


def parseConfigurationFile( configFilepath ):
	with open( configFilepath, 'r' ) as configFile:
		configContents = configFile.read()

	# Prepare default values (just in case they're not defined in the config file)
	configuration = OrderedDict([ ('threshold', 40), ('centerImageXOffset', 0), ('centerImageYOffset', 0), ('centerImageScaling', 1.0),
								('sideImagesXOffset', 0), ('sideImagesYOffset', 0), ('sideImagesScaling', 1.0), ('reverseSides', False ) ])

	for line in configContents.splitlines():
		if line.startswith( '#' ): continue

		if ':' in line:
			parameter, value = line.split(':')
			parameter = parameter.strip()

			if parameter in configuration and value.strip() != '':
				if 'Scaling' in line: configuration[parameter] = float( value )
				elif 'reverse' in line: configuration[parameter] = stringToBool( value )
				else: configuration[parameter] = int( value )

	return configuration


def getConfigurationFromCmd( args ):
	if args.mode == 'cmd':

		configuration = OrderedDict([ ('threshold', int(args.threshold) ), 
									  ( 'centerImageXOffset', int(args.centerImageXOffset) ), 
									  ( 'centerImageYOffset', int(args.centerImageYOffset) ), 
									  ( 'centerImageScaling', float(args.centerImageScaling )),
									  ( 'sideImagesXOffset', int(args.sideImagesXOffset) ), 
									  ( 'sideImagesYOffset', int(args.sideImagesYOffset) ), 
									  ( 'sideImagesScaling', float(args.sideImagesScaling) ),
									  ( 'reverseSides', stringToBool(args.reverseSides) ) ])
	elif args.mode == 'cmd-config': 
		configuration = parseConfigurationFile( args.configFile )

	return configuration


def beginGimpAutomationCmd( leftImagePaths, centerImagePaths, rightImagePaths, maskImagePath, configFilePath, outputPath, configuration, saveHighRes ):
	#gimpExeFolder, gimpExeName = determineExePath()
	if not gimpExeFolder: return

	# Get the length of the shortest list, this will be how many CSPs will be created
	cspsToCreate = 0
	for pathsList in ( leftImagePaths, centerImagePaths, rightImagePaths ):
		totalImages = len( pathsList )

		if cspsToCreate == 0 or totalImages < cspsToCreate: cspsToCreate = totalImages

	print '\n\nTotal CSPs to create:', cspsToCreate

	# Separate out the "extra" images that will not be processed
	extraImages = []
	leftImagePaths = leftImagePaths[:cspsToCreate]
	centerImagePaths = centerImagePaths[:cspsToCreate]
	rightImagePaths = rightImagePaths[:cspsToCreate]
	extraImages.extend( leftImagePaths[cspsToCreate:] )
	extraImages.extend( centerImagePaths[cspsToCreate:] )
	extraImages.extend( rightImagePaths[cspsToCreate:] )

	maskImagePath = preparePathForGimpCmd( maskImagePath )
	configFilePath = preparePathForGimpCmd( configFilePath )
	outputPath = preparePathForGimpCmd( outputPath )

	for i in range( cspsToCreate ):

		if not os.path.exists( leftImagePaths[i] ) or not os.path.exists( centerImagePaths[i] ) or not os.path.exists( rightImagePaths[i] ):
			print '\nImage set ' + str(i+1) + ' could not be processed because one of the images in the set could not be found.'
			continue

		leftImagePath = preparePathForGimpCmd( leftImagePaths[i] )
		centerImagePath = preparePathForGimpCmd( centerImagePaths[i] )
		rightImagePath = preparePathForGimpCmd( rightImagePaths[i] )

		returnCode, outputStream = callGimpAutomation( gimpExeFolder, gimpExeName, leftImagePath, centerImagePath, rightImagePath, maskImagePath, configFilePath, outputPath, configuration, saveHighRes )
		
		if returnCode == 0:
			print '\nFinished processing group ' + str(i+1) + '.', outputStream
		else:
			print '\nUnable to process group ' + str(i+1) + ';', outputStream
			print 'Return code: ', returnCode

	return extraImages


def preparePathForGimpCmd( originalFilepath ):
	#if ':' not in originalFilepath:  # Probably a relative path.
	return originalFilepath.replace('\\', '/')


def determineExePath():

	""" Determines the absolute file path to the GIMP console executable 
		(the exe itself varies based on program version). """
	
	# Check for the expected program folder
	gimpBinaryDirectory = "C:\\Program Files\\GIMP 2\\bin"
	if not os.path.exists( gimpBinaryDirectory ):
		print 'GIMP does not appear to be installed; unable to find the GIMP program directory.'
		return None, None
	
	# Check the files in the program folder for a 'console' executable
	for fileOrFolderName in os.listdir( gimpBinaryDirectory ):
		if fileOrFolderName.startswith( 'gimp-console' ) and fileOrFolderName.endswith( '.exe' ):
			return gimpBinaryDirectory, fileOrFolderName

	else: # The loop above didn't break; unable to find the exe
		print 'Unable to find the GIMP console executable.'
		return None, None


def callGimpAutomation( gimpExeFolder, gimpExeName, leftImagePath, centerImagePath, rightImagePath, maskImagePath, configFilePath, outputPath, configuration, saveHighRes ):
	
	# Create a list of the configuration's values, converted to strings
	gimpFunctionArgsList = []
	for parameter, value in configuration.items():
		if parameter != 'reverseSides': gimpFunctionArgsList.append( str(value) )

	# Convert the boolean flags to strings
	if configuration['reverseSides']: reverseSidesFlag = '1'
	else: reverseSidesFlag = '0'
	if saveHighRes: saveHighResFlag = '1'
	else: saveHighResFlag = '0'

	# :: Construct the command. GIMP Options are:
	# :: -d = "--no-data", prevents loading of brushes, gradients, palettes, patterns, ...
	# :: -f = "--no-fonts", prevents loading of fonts
	# :: -i = "--no-interface", prevents loading of interface
	# :: -g = "--gimprc", applies setting preferences. Must be a full path. In this case, it is just used to suppress exporting a color profile
	# :: -b "" specifies a script-fu command to be run in gimp

	command = (
		'start /B /D "{}"'.format( gimpExeFolder ) # Starts a new process. /B prevents creating a new window, and /D sets the working directory
		+ ' {} -d -f -i -g "{}"'.format( gimpExeName, scriptHomeFolder + '/gimprcTCC' ) # Call the gimp executable with the arguments described above
		+ ' -b "(python-fu-create-tri-csp 1' # Extra param, "1", to run in NON-INTERACTIVE mode
		' \\"' + leftImagePath + '\\"'
		' \\"' + centerImagePath + '\\"'
		' \\"' + rightImagePath + '\\"'
		' \\"' + maskImagePath + '\\"'
		' \\"' + configFilePath + '\\"'
		' \\"' + outputPath + '\\" '
		+ ' '.join( gimpFunctionArgsList ) + ' ' + reverseSidesFlag + ' ' + saveHighResFlag + ' 0)" -b "(gimp-quit 0)"'
	)

	print '\nCommand to Execute:\n', command
	
	return cmdChannel( command )


def cmdChannel( command, standardInput=None, shell=True ): 
	
	""" IPC (Inter-Process Communication) to command line. """

	process = subprocess.Popen( command, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) #, creationflags=0x08000000
	stdout_data, stderr_data = process.communicate( input=standardInput )

	if process.returncode == 0: return ( process.returncode, stdout_data )
	else: return ( process.returncode, stderr_data )


def getGimpProgramVersion():
	_, versionText = cmdChannel( 'start /B /D "{}" {} --version'.format(gimpExeFolder, gimpExeName) )
	return versionText.split()[-1]


def getGimpPluginDirectory( gimpVersion ):

	""" Checks known directory paths for GIMP versions 2.8 and 2.10. If both appear 
		to be installed, we'll check the version of the executable that was found. """

	userFolder = os.path.expanduser('~') # Resolves to "C:\Users\[userName]"
	v8_Path = os.path.join( userFolder, '.gimp-2.8\\plug-ins' )
	v10_Path = os.path.join( userFolder, 'AppData\\Roaming\\GIMP\\2.10\\plug-ins' )

	if os.path.exists( v8_Path ) and os.path.exists( v10_Path ):
		# Both versions seem to be installed. Use Gimp's version to decide which to use
		major, minor, _ = gimpVersion.split( '.' )
		if major != '2':
			return ''
		if minor == '8':
			return v8_Path
		else:
			return v10_Path

	elif os.path.exists( v8_Path ): return v8_Path
	elif os.path.exists( v10_Path ): return v10_Path
	else: return ''


def getScriptVersion( pluginDir, scriptFile ):

	""" Scans the script for a line like "version = 2.2\n" and parses it. """

	scriptPath = os.path.join( pluginDir, scriptFile )

	if os.path.exists( scriptPath ):
		with open( scriptPath, 'r' ) as script:
			for line in script:
				line = line.strip()

				if line.startswith( 'version' ) and '=' in line:
					return line.split( '=' )[-1].strip()
		
	return '-1'


if "__main__" in __name__:
	scriptHomeFolder = os.path.abspath( os.path.dirname(sys.argv[0]) ) # Can't use __file__ after freeze
	gimpExeFolder, gimpExeName = determineExePath()
	gimpVersion = getGimpProgramVersion()
	pluginDir = getGimpPluginDirectory( gimpVersion )

	# Check that the required GIMP modules are installed, and get their versions
	if not gimpExeFolder or not pluginDir:
		print 'Unable to locate the GIMP plug-in directory. Are you sure GIMP is installed?'
		print "\nPress 'Enter' to exit."
		raw_input()
		exit()
	else:
		createCspScriptVersion = getScriptVersion( pluginDir, 'python-fu-create-tri-csp.py' )
		finishCspScriptVersion = getScriptVersion( pluginDir, 'python-fu-finish-csp.py' )
		# may also check existance with "pdb.gimp_procedural_db_proc_exists('python-fu-create-tri-csp')", which returns a bool

		# Make sure the GIMP plug-ins were detected
		if createCspScriptVersion == '-1' or finishCspScriptVersion == '-1':
			if createCspScriptVersion == '-1' and finishCspScriptVersion == '-1':
				print "Unable to locate the GIMP plug-ins. Are you sure they're installed?"
			elif createCspScriptVersion == '-1':
				print "Unable to locate the 'python-fu-create-tri-csp.py' plug-in. Are you sure it's installed?"
			elif finishCspScriptVersion == '-1':
				print "Unable to locate the 'python-fu-finish-csp.py' plug-in. Are you sure it's installed?"

			print "\nPress 'Enter' to exit."
			raw_input()
			exit()

		# Print out version info
		print ''
		print '            Version info:'
		print ''
		print '  GIMP:                    ', gimpVersion
		print '  Tri-CSP Creator:         ', programVersion
		print '  create-tri-csp script:   ', createCspScriptVersion
		print '  finish-csp script:       ', finishCspScriptVersion
		print ''
		print 'GIMP executable directory: ', gimpExeFolder
		print 'GIMP Plug-ins directory:   ', pluginDir
		print ''

	# Check for arguments passed to the program. If there are none, default to using the GUI
	if not len( sys.argv ) > 1: initializeGui()
	else:
		args = parseArguments()

		if args.mode == 'cmd' or args.mode == 'cmd-config': # All input required should be provided via command line; go strait to the processing
			configuration = getConfigurationFromCmd( args )

			beginGimpAutomationCmd( args.leftImagePaths, 
									args.centerImagePaths, 
									args.rightImagePaths,
									args.maskImagePath, 
									'', 
									args.outputPath, 
									configuration, 
									args.saveHighRes )

		else: initializeGui()