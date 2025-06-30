import customtkinter as ctk
from tkinter import messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
from tkcalendar import DateEntry  # Import DateEntry for date picker
import datetime

# App Configuration
ctk.set_appearance_mode("Light")  # Default theme
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Event Planning and Expense Splitting")
app.geometry("1000x700")

# Global Variables
current_frame = None
events = []  # List of events
current_event = {}  # Active event for viewing/editing

# Creating content frames first 
home_content = ctk.CTkFrame(app)
create_event_content = ctk.CTkFrame(app)
add_expense_content = ctk.CTkFrame(app)
calculate_debts_content = ctk.CTkFrame(app)
view_charts_content = ctk.CTkFrame(app)

# Function to switch between frames
def switch_frame(new_frame):
    """
    Switches between different frames in the application.
    Hides the current frame and displays the new one.
    
    Args:
        new_frame: The frame to switch to
    """
    global current_frame
    if current_frame:
        current_frame.pack_forget()
    new_frame.pack(fill="both", expand=True, padx=20, pady=20)
    current_frame = new_frame

# Home screen function
def home_frame():
    """
    Displays the home screen showing all events and the currently selected event.
    Lists all created events and allows selecting one to make it the current event.
    """
    switch_frame(home_content)
    for widget in home_content.winfo_children():
        widget.destroy()
        
    ctk.CTkLabel(home_content, text="Event Planning and Expense Splitting", font=("Arial", 24)).pack(pady=20)
    ctk.CTkLabel(home_content, text="Welcome! Use the navigation panel to manage your events and expenses.", 
                font=("Arial", 16)).pack(pady=10)
    
    if events:
        ctk.CTkLabel(home_content, text="Your Events:", font=("Arial", 18)).pack(pady=10)
        events_frame = ctk.CTkFrame(home_content)
        events_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for i, event in enumerate(events):
            event_frame = ctk.CTkFrame(events_frame)
            event_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(event_frame, text=f"{event['name']} ({event['date']})", font=("Arial", 14)).pack(side="left", padx=10)
            
            def select_event(e=event):
                global current_event
                current_event = e
                home_frame()
                
            ctk.CTkButton(event_frame, text="Select", command=select_event, width=80).pack(side="right", padx=10)
    else:
        ctk.CTkLabel(home_content, text="No events created yet..... Create an event to get started!", 
                    font=("Arial", 16)).pack(pady=50)
    
    if current_event:
        current_event_frame = ctk.CTkFrame(home_content)
        current_event_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(current_event_frame, text=f"Current Event: {current_event['name']}", 
                    font=("Arial", 18)).pack(pady=10)
        ctk.CTkLabel(current_event_frame, text=f"Date: {current_event['date']}").pack(pady=5)
        ctk.CTkLabel(current_event_frame, text=f"Members: {', '.join(current_event['members'])}").pack(pady=5)
        ctk.CTkLabel(current_event_frame, text=f"Total Expenses: {len(current_event.get('expenses', []))}").pack(pady=5)

# Create event function with date picker
def create_event_frame():
    """
    Creates a new event with a name, date (using date picker), and members list.
    Uses DateEntry widget for selecting dates to prevent format errors.
    """
    switch_frame(create_event_content)
    for widget in create_event_content.winfo_children():
        widget.destroy()

    ctk.CTkLabel(create_event_content, text="Create Event", font=("Arial", 20)).pack(pady=10)

    event_name_var = ctk.StringVar()
    members_var = ctk.StringVar()

    # Event name input
    ctk.CTkLabel(create_event_content, text="Event Name:").pack(pady=5)
    ctk.CTkEntry(create_event_content, textvariable=event_name_var).pack(pady=5)

    # Date picker frame
    date_frame = ctk.CTkFrame(create_event_content)
    date_frame.pack(pady=10)
    
    ctk.CTkLabel(date_frame, text="Event Date:").pack(side="left", padx=5)
    
    # Create a wrapper frame for the DateEntry widget
    date_picker_frame = ctk.CTkFrame(date_frame)
    date_picker_frame.pack(side="left", padx=5)
    
    # Add the DateEntry widget (tkinter native widget)
    date_picker = DateEntry(date_picker_frame, width=12, background='darkblue',
                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    date_picker.pack(pady=5, padx=5)

    # Members input (renamed from participants)
    ctk.CTkLabel(create_event_content, text="Members (comma-separated):").pack(pady=5)
    ctk.CTkEntry(create_event_content, textvariable=members_var).pack(pady=5)

    def submit_event():
        """Validates and creates a new event with the entered information"""
        event_name = event_name_var.get()
        event_date = date_picker.get_date().strftime('%Y-%m-%d')  # Format date properly
        members = members_var.get()

        if not event_name or not members:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        global current_event
        current_event = {
            "name": event_name,
            "date": event_date,
            "members": [m.strip() for m in members.split(",")],  # Renamed from participants to members
            "expenses": [],
        }
        events.append(current_event)
        messagebox.showinfo("Success", f"Event '{event_name}' created successfully!")
        home_frame()

    ctk.CTkButton(create_event_content, text="Submit", command=submit_event, fg_color="green").pack(pady=20)
    ctk.CTkButton(create_event_content, text="Back to Home", command=home_frame).pack(pady=5)

# Add expense function with Members terminology
def add_expense_frame():
    """
    Allows adding expenses to the current event.
    The expense includes type, amount, payer, and members involved.
    
    Uses checkboxes to select which members are involved in each expense.
    """
    if not current_event:
        messagebox.showerror("Error", "Please create or select an event first!")
        home_frame()
        return
        
    switch_frame(add_expense_content)
    for widget in add_expense_content.winfo_children():
        widget.destroy()

    ctk.CTkLabel(add_expense_content, text="Add Expense", font=("Arial", 20)).pack(pady=10)
    ctk.CTkLabel(add_expense_content, text=f"Event: {current_event['name']}", font=("Arial", 16)).pack(pady=5)

    # Create variables for expense information
    expense_type_var = ctk.StringVar(value="Food")  # Set default value
    expense_amount_var = ctk.StringVar()  # Using StringVar for better error handling
    paid_by_var = ctk.StringVar()

    # Expense type selector
    ctk.CTkLabel(add_expense_content, text="Expense Type:").pack(pady=5)
    ctk.CTkOptionMenu(add_expense_content, values=["Food", "Accommodation", "Transportation", "Entertainment", "Other"], 
                     variable=expense_type_var).pack(pady=5)

    # Amount input
    ctk.CTkLabel(add_expense_content, text="Amount:").pack(pady=5)
    ctk.CTkEntry(add_expense_content, textvariable=expense_amount_var).pack(pady=5)

    # Paid by selector (dropdown with members)
    ctk.CTkLabel(add_expense_content, text="Paid By:").pack(pady=5)
    payer_menu = ctk.CTkOptionMenu(add_expense_content, values=current_event["members"], variable=paid_by_var)
    payer_menu.pack(pady=5)
    if current_event["members"]:
        paid_by_var.set(current_event["members"][0])

    # Members involved selector (checkboxes)
    ctk.CTkLabel(add_expense_content, text="Members Involved:").pack(pady=5)
    
    members_frame = ctk.CTkFrame(add_expense_content)
    members_frame.pack(pady=10)
    
    # Create checkboxes for each member
    member_vars = {}
    for member in current_event["members"]:
        var = ctk.BooleanVar(value=True)  # Default all members to selected
        member_vars[member] = var
        ctk.CTkCheckBox(members_frame, text=member, variable=var).pack(anchor="w", pady=2)

    def submit_expense():
        """Validates and adds a new expense to the current event"""
        expense_type = expense_type_var.get()
        
        # Validate amount is a positive number
        try:
            amount = float(expense_amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for amount!")
            return
            
        paid_by = paid_by_var.get()
        
        # Get selected members
        selected_members = [m for m, var in member_vars.items() if var.get()]
        
        # Validate all fields are filled
        if not expense_type or not amount or not paid_by or not selected_members:
            messagebox.showerror("Error", "Please fill in all fields and select at least one member!")
            return

        # Create expense dictionary
        expense = {
            "type": expense_type,
            "amount": amount,
            "paid_by": paid_by,
            "participants": selected_members,  # Keep internal key as participants for backward compatibility
        }
        current_event["expenses"].append(expense)
        messagebox.showinfo("Success", f"Expense '{expense_type}' added successfully!")
        
        # Clear fields for next entry
        expense_amount_var.set("")
        
        # Keep the form open for additional expenses

    # Button frame
    buttons_frame = ctk.CTkFrame(add_expense_content)
    buttons_frame.pack(pady=20)
    
    ctk.CTkButton(buttons_frame, text="Submit Expense", command=submit_expense, fg_color="yellow").pack(side="left", padx=10)
    ctk.CTkButton(buttons_frame, text="Back to Home", command=home_frame).pack(side="left", padx=10)

# OPTIMIZED DEBT CALCULATION FUNCTION
# This is the new shared function that calculates debts to avoid code duplication
def calculate_member_debts(event):
    """
    Calculates the debt balances for each member in an event.
    
    Args:
        event: The event dictionary containing expenses and members
        
    Returns:
        tuple: (member_debts, settlement_plan)
            - member_debts: Dictionary with members as keys and their balance as values
            - settlement_plan: List of tuples (payer, receiver, amount) for settlement
    """
    # Initialize debts dictionary for all members
    member_debts = {member: 0 for member in event["members"]}
    
    # Skip calculation if no expenses
    if not event.get("expenses"):
        return member_debts, []
    
    # Process each expense to calculate individual shares
    for expense in event["expenses"]:
        num_participants = len(expense["participants"])
        # Skip if no participants to avoid division by zero
        if num_participants == 0:
            continue
            
        # Calculate individual share for this expense
        share_per_person = expense["amount"] / num_participants
        
        # Subtract share from each participant (they owe this amount)
        for participant in expense["participants"]:
            member_debts[participant] -= share_per_person
        
        # Add full amount to payer (they paid this amount)
        member_debts[expense["paid_by"]] += expense["amount"]
    
    # Calculate optimized settlement plan
    settlement_plan = []
    
    # Separate members into payers (who owe money) and receivers (who are owed money)
    net_payers = [(m, b) for m, b in member_debts.items() if b < 0]  # Negative balance = owes money
    net_receivers = [(m, b) for m, b in member_debts.items() if b > 0]  # Positive balance = should receive money
    
    # Sort by amount to optimize payments
    net_payers.sort(key=lambda x: x[1])  # Sort by amount (ascending)
    net_receivers.sort(key=lambda x: x[1], reverse=True)  # Sort by amount (descending)
    
    # Create optimized payment plan by matching payers with receivers
    i, j = 0, 0
    while i < len(net_payers) and j < len(net_receivers):
        payer, payer_amount = net_payers[i]
        receiver, receiver_amount = net_receivers[j]
        
        # Calculate payment amount (minimum of what's owed and what's receivable)
        payment = min(abs(payer_amount), receiver_amount)
        if payment > 0.01:  # Ignore very small payments (less than 0.01)
            settlement_plan.append((payer, receiver, payment))
        
        # Update balances
        net_payers[i] = (payer, payer_amount + payment)
        net_receivers[j] = (receiver, receiver_amount - payment)
        
        # Move to next person if their balance is close to zero
        if abs(net_payers[i][1]) < 0.01:
            i += 1
        if abs(net_receivers[j][1]) < 0.01:
            j += 1
    
    return member_debts, settlement_plan

# Modified calculate_debts_frame to use the shared function
def calculate_debts_frame():
    """
    Calculates who owes money to whom based on expenses.
    Shows a settlement plan to minimize the number of transactions.
    
    Displays detailed information on members' balances and who needs to pay whom.
    """
    # Check if an event is selected
    if not current_event:
        messagebox.showerror("Error", "Please create or select an event first!")
        home_frame()
        return
        
    # Switch to the debts calculation frame
    switch_frame(calculate_debts_content)
    for widget in calculate_debts_content.winfo_children():
        widget.destroy()

    # Display header
    ctk.CTkLabel(calculate_debts_content, text="Who Owes How Much to Whom", font=("Arial", 20)).pack(pady=10)
    ctk.CTkLabel(calculate_debts_content, text=f"Event: {current_event['name']}", font=("Arial", 16)).pack(pady=5)

    # Check if there are any expenses
    if not current_event.get("expenses"):
        ctk.CTkLabel(calculate_debts_content, text="No expenses recorded yet.", font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(calculate_debts_content, text="Back to Home", command=home_frame).pack(pady=10)
        return

    # Calculate debts using the shared function
    member_debts, settlement_plan = calculate_member_debts(current_event)

    # Create results display textbox
    result_text = ctk.CTkTextbox(calculate_debts_content, wrap="word", font=("Arial", 14), height=200)
    result_text.pack(fill="both", expand=True, padx=20, pady=10)
    result_text.insert("1.0", "Debts Summary:\n\n")

    # Show each member's balance
    for member, balance in member_debts.items():
        if balance > 0:
            result_text.insert("end", f"{member} needs to receive Rs.{balance:.2f}\n")
        elif balance < 0:
            result_text.insert("end", f"{member} owes Rs.{abs(balance):.2f}\n")
        else:
            result_text.insert("end", f"{member} is settled up.\n")
    
    result_text.insert("end", "\nDetailed Settlement Plan:\n\n")
    
    # Display the settlement plan
    if not settlement_plan:
        result_text.insert("end", "Everyone is settled up already!\n")
    else:
        for payer, receiver, amount in settlement_plan:
            result_text.insert("end", f"{payer} pays Rs.{amount:.2f} to {receiver}\n")

    # Disable editing of the text box
    result_text.configure(state="disabled")
    
    # Add back button
    ctk.CTkButton(calculate_debts_content, text="Back to Home", command=home_frame).pack(pady=10)

# View charts function with Members terminology
def view_charts_frame():
    """
    Displays visualization charts for expenses.
    Shows both bar chart and pie chart of expenses by type.
    """
    if not current_event:
        messagebox.showerror("Error", "Please create or select an event first!")
        home_frame()
        return
        
    switch_frame(view_charts_content)
    for widget in view_charts_content.winfo_children():
        widget.destroy()

    ctk.CTkLabel(view_charts_content, text="Expense Charts", font=("Arial", 20)).pack(pady=10)
    ctk.CTkLabel(view_charts_content, text=f"Event: {current_event['name']}", font=("Arial", 16)).pack(pady=5)

    if not current_event.get("expenses"):
        ctk.CTkLabel(view_charts_content, text="No expenses recorded yet.", font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(view_charts_content, text="Back to Home", command=home_frame).pack(pady=10)
        return

    # Group expenses by type
    expense_by_type = {}
    for expense in current_event["expenses"]:
        expense_type = expense["type"]
        if expense_type not in expense_by_type:
            expense_by_type[expense_type] = 0
        expense_by_type[expense_type] += expense["amount"]
    
    expense_types = list(expense_by_type.keys())
    expense_amounts = list(expense_by_type.values())

    # Create figure with two subplots
    fig = Figure(figsize=(10, 8), dpi=100)
    
    # Bar chart - top subplot
    ax1 = fig.add_subplot(211)
    ax1.bar(expense_types, expense_amounts, color="skyblue")
    ax1.set_title("Expense Distribution by Type")
    ax1.set_ylabel("Amount (Rs.)")
    ax1.set_xlabel("Expense Type")
    
    # Pie chart - bottom subplot
    ax2 = fig.add_subplot(212)
    ax2.pie(expense_amounts, labels=expense_types, autopct='%1.1f%%', startangle=90, shadow=True)
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax2.set_title("Expense Percentage by Type")
    
    fig.tight_layout()  # Adjust layout to not overlap

    # Display the chart
    chart_canvas = FigureCanvasTkAgg(fig, view_charts_content)
    chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    ctk.CTkButton(view_charts_content, text="Back to Home", command=home_frame).pack(pady=10)

# Export to PDF function (optimized to use the shared debt calculation)
def export_to_pdf():
    """
    Exports all event details, expenses and settlement plan to a PDF file.
    User can choose where to save the file.
    """
    # Check if an event is selected
    if not current_event:
        messagebox.showerror("Error", "Please create or select an event first!")
        return
        
    # Check if there are expenses to export
    if not current_event.get("expenses"):
        messagebox.showerror("Error", "No expenses recorded to export.")
        return

    # Calculate debts using the shared function
    member_debts, settlement_plan = calculate_member_debts(current_event)

    # Create a PDF document
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"Event Expense Report: {current_event['name']}", ln=True, align="C")
    pdf.ln(5)
    
    # Add event details
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Event Details:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Event Name: {current_event['name']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {current_event['date']}", ln=True)
    pdf.cell(200, 10, txt="Members: " + ", ".join(current_event["members"]), ln=True)
    pdf.ln(5)

    # Add expenses
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Expenses:", ln=True)
    pdf.set_font("Arial", size=12)
    
    if not current_event["expenses"]:
        pdf.cell(200, 10, txt="No expenses recorded.", ln=True)
    else:
        # Create expense table headers
        pdf.set_font("Arial", style="B", size=10)
        pdf.cell(40, 10, txt="Type", border=1)
        pdf.cell(30, 10, txt="Amount (Rs.)", border=1)
        pdf.cell(40, 10, txt="Paid By", border=1)
        pdf.cell(80, 10, txt="Members Involved", border=1, ln=True)
        
        # Add expense data
        pdf.set_font("Arial", size=10)
        for expense in current_event["expenses"]:
            pdf.cell(40, 10, txt=expense["type"], border=1)
            pdf.cell(30, 10, txt=f"{expense['amount']:.2f}", border=1)
            pdf.cell(40, 10, txt=expense["paid_by"], border=1)
            
            # Handle long member lists by truncating if necessary
            members_str = ", ".join(expense["participants"])
            if len(members_str) > 40:
                members_str = members_str[:37] + "..."
            pdf.cell(80, 10, txt=members_str, border=1, ln=True)
    
    pdf.ln(10)

    # Add debts summary
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Debts Summary:", ln=True)
    pdf.set_font("Arial", size=12)
    
    # Display member balances
    for member, balance in member_debts.items():
        if balance > 0:
            pdf.cell(200, 10, txt=f"{member} needs to receive Rs.{balance:.2f}", ln=True)
        elif balance < 0:
            pdf.cell(200, 10, txt=f"{member} owes Rs.{abs(balance):.2f}", ln=True)
        else:
            pdf.cell(200, 10, txt=f"{member} is settled up.", ln=True)
    
    pdf.ln(5)
    
    # Add settlement plan
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Settlement Plan:", ln=True)
    pdf.set_font("Arial", size=12)
    
    # Display the settlement plan
    if not settlement_plan:
        pdf.cell(200, 10, txt="Everyone is settled up already!", ln=True)
    else:
        for payer, receiver, amount in settlement_plan:
            pdf.cell(200, 10, txt=f"{payer} pays Rs.{amount:.2f} to {receiver}", ln=True)

    # Prompt user to save the file
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        pdf.output(file_path)
        messagebox.showinfo("Success", f"PDF exported to {file_path}")

# Exit application function
def exit_app():
    """Confirms if the user wants to exit and closes the application if confirmed"""
    if messagebox.askokcancel("Exit", "Are you sure you want to exit? All unsaved data will be lost."):
        app.destroy()

# Initialize home content
ctk.CTkLabel(home_content, text="Event Planning and Expense Splitting", font=("Arial", 24)).pack(pady=20)
ctk.CTkLabel(home_content, text="Welcome! Use the navigation panel to manage your events and expenses.", 
            font=("Arial", 16)).pack(pady=10)
ctk.CTkLabel(home_content, text="No events created yet. Create an event to get started!", 
            font=("Arial", 16)).pack(pady=50)

# Navigation Panel
nav_panel = ctk.CTkFrame(app, width=200, corner_radius=15)
nav_panel.pack(side="left", fill="y", padx=10, pady=10)

# Navigation buttons
ctk.CTkButton(nav_panel, text="Home", command=home_frame, fg_color="#4CAF50", corner_radius=10).pack(pady=10, padx=10)
ctk.CTkButton(nav_panel, text="Create Event", command=create_event_frame, fg_color="#4CAF50", corner_radius=10).pack(pady=10, padx=10)
ctk.CTkButton(nav_panel, text="Add Expense", command=add_expense_frame, fg_color="#FFC107", corner_radius=10).pack(pady=10, padx=10)
ctk.CTkButton(nav_panel, text="View Charts", command=view_charts_frame, fg_color="#2196F3", corner_radius=10).pack(pady=10, padx=10)
ctk.CTkButton(nav_panel, text="Calculate Debts", command=calculate_debts_frame, fg_color="#8E44AD", corner_radius=10).pack(pady=10, padx=10)
ctk.CTkButton(nav_panel, text="Export to PDF", command=export_to_pdf, fg_color="#F44336", corner_radius=10).pack(pady=10, padx=10)
ctk.CTkButton(nav_panel, text="Exit", command=exit_app, fg_color="#607D8B", corner_radius=10).pack(pady=10, padx=10)

# Set default frame
home_frame()

# Run App
app.mainloop()