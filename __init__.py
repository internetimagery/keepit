import maya.cmds as cmds

def main():
    """ Perform an archive save! """
    result = cmds.promptDialog(
		title='Rename Object',
		message='Enter Name:',
		button=None)

    # result = cmds.promptDialog(
	# 	title='Rename Object',
	# 	message='Enter Name:',
	# 	button=['OK', 'Cancel'],
	# 	defaultButton='OK',
	# 	cancelButton='Cancel',
	# 	dismissString='Cancel')
    # if result == 'OK':
    # 	print cmds.promptDialog(query=True, text=True)
