import board

if board.board_id == "unexpectedmaker_tinys3":
    from tinys3 import TinyS3Support
    hardware = TinyS3Support()
else:
    hardware = None
