inventory = []
def insert_product():
  while True:
      code = input("รหัสสินค้า : ")
      is_duplicate = False
      for item in inventory:
          if item['code'] == code:
              is_duplicate = True
              break

      if is_duplicate:
          print("มีสินค้าอยู่แล้ว")
      else:
          name = input("ชื่อสินค้า : ")

          quantity = int(input("จำนวนว : "))

          product_id = len(inventory) + 1

          new_item = {
              "id": product_id,
              "code": code,
              "name": name,
              "quantity": quantity
          }
          inventory.append(new_item)
          print("เพิ่มสินค้าสำเร็จ")
          break
