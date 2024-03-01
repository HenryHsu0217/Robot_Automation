from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    order=get_orders()
    order_numbers=order.group_by_column("Order number")
    page=browser.page()
    for order_number in order_numbers:
        for orders in order_number:
            order_num=orders["Order number"]
            close_annoying_modal()
            fill_the_form(orders)
            store_receipt_as_pdf(order_num)
            screenshot_robot(order_num)
            embed_screenshot_to_receipt(f"output/{order_num}.png",f"output/order_{order_num}.pdf")
            page.click("text='Order another robot'")

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv")
    orders = Tables()
    Orders = orders.read_table_from_csv("orders.csv", columns=["Order number", "Head" ,"Body", "Legs","Address"])
    return Orders
def close_annoying_modal():
    page=browser.page()
    page.click("text='OK'")
    return page
def fill_the_form(order):
    page=browser.page()
    Head=order["Head"]
    Body=order["Body"]
    Leg=order["Legs"]
    Address=order["Address"]
    page.select_option("#head",Head)
    page.check(f"#id-body-{Body}")
    page.fill("input[placeholder='Enter the part number for the legs']",Leg)
    page.fill("#address",Address)
    page.click("text='Preview'")
    page.click("text='Order'")
    alerts = page.evaluate("""() => {
    const elements = document.querySelectorAll('.alert.alert-danger');
    return elements.length > 0;
}""")
    while alerts:
        page.click("text='Order'")
        alerts = page.evaluate("""() => {
    const elements = document.querySelectorAll('.alert.alert-danger');
    return elements.length > 0;
}""")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    html=page.locator("#receipt").inner_html()
    print("Saving PDF")
    pdf=PDF()
    pdf.html_to_pdf(html, f"output/order_{order_number}.pdf")
def screenshot_robot(order_number):
    page=browser.page()
    element = page.query_selector("#robot-preview-image")
    element.screenshot(path=f"output/{order_number}.png")
def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf=PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot,source_path=pdf_file, output_path=pdf_file)