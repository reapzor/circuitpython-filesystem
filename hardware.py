import board

if board.board_id == "unexpectedmaker_tinys3":
    from tinys3 import TinyS3Support
    hardware = TinyS3Support()
elif "espressif_esp32s3_devkitc" in board.board_id:
    from s3_dev_kit import S3DevKitSupport
    hardware = S3DevKitSupport()
else:
    print(f"Unknown board: {board.board_id}")
    hardware = None
