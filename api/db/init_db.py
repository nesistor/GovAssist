from api.services.embedding_service import add_documents_to_collection

documents = {
    "dmv": [
        "This is a document about getting a driver's license.",
        "Here are the requirements for vehicle registration in California. "
        "You'll need to provide proof of insurance and a smog certificate. "
        "The process can be completed online or at a DMV office. "
        "Make sure you have all the necessary documents before starting the process.",
        "This document explains vehicle registration. "
        "To register your vehicle, you will need to complete an application form, "
        "provide proof of ownership, and pay the registration fee. "
        "You may also need to have your vehicle inspected for emissions compliance.",
        "Renewing your driver's license can often be done online. "
        "Check the DMV website for eligibility. You'll need your current license number and may need to pass an eye exam.",
        "If you've lost your driver's license, you'll need to apply for a replacement. "
        "This usually involves filling out a form and paying a fee. "
        "You may need to visit a DMV office in person to verify your identity."
    ],
    "tax": [
        "This document provides information on income tax brackets.",
        "Here's a guide to filing your taxes online. "
        "Make sure you have all your income statements (W-2, 1099, etc.) before you begin. "
        "You can use tax software or consult with a tax professional to help you file accurately. "
        "Remember to keep records of your tax returns and supporting documents.",
        "This is a guide to filing your taxes online. "
        "You can use various online tax filing services or the IRS website. "
        "Ensure you have your Social Security number, W-2s, and other relevant tax documents. "
        "E-filing is generally faster and more secure than paper filing.",
        "Understanding tax brackets is crucial for estimating your tax liability. "
        "Tax brackets are based on your taxable income and filing status. "
        "Higher income generally falls into higher tax brackets.",
        "Tax deductions can reduce your taxable income. "
        "Common deductions include mortgage interest, student loan interest, and charitable contributions. "
        "Keep records of your expenses to claim the appropriate deductions."
    ]
}

if __name__ == "__main__":
    add_documents_to_collection(documents)
    print("Documents added to collection.")