##### Baseline Imports START (Do Not Edit) #####
from pathlib import Path
from datetime import datetime
from shiny import App, ui, render, reactive, req
from shiny.types import ImgData
import os
from faicons import icon_svg
##### Baseline Imports END #####

##### Resource and Version Info START #####
resource_dir = Path(__file__).parent / "www" # Do Not Edit
Web_app_version = "Version: 0.0.0" # Edit as Required
##### Resource and Version Info END #####

home_tab_content = ui.div(
    ui.h2("Welcome to Home Tab"),
    ui.p("This content is shown when Home is selected.")
)
settings_tab_content = ui.div(
ui.h2("Settings Panel"),
ui.p("This content is shown when Settings is selected.")
)
reports_tab_content = ui.div(
ui.h2("Reports Dashboard"),
ui.p("This content is shown when Reports is selected.")
)
feedback_tab_content = ui.div(
    ui.card(
        ui.card_header(ui.h3("WebApp Feedback", style="color: #12375b;font-weight:bold;")),
        ui.p("If you encounter an issue or have suggestions for how to improve this WebApp, please fill in the form below and click Submit. This will open a prepared email, for you to send. Thank you!"),
        ui.input_select(id="feedback_type_id", label="Please select:", choices=["Report an Issue", "Log a Suggestion"], multiple=False, width="25%"),
        ui.input_text(id="feedback_webapp_name_id", label="Provide the WebApp name:", value="", width="50%"),
        ui.row(
            ui.column(9,
                ui.input_text_area(id="feedback_details_id", label="Describe the Issue or Suggestion:", value="", width="100%", height="140px")
            ),
            ui.column(3,
                ui.output_ui(id="submit_feedback_ui_id")
            )     
        )
    )
)

##### UI Definition START #####
app_ui = ui.page_fillable(
    ##### WebApp Styling START (Do Not Edit) #####
    # External stylesheets
    ui.tags.link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Montserrat"),
    ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"),
    ui.tags.link(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"),
    ui.head_content(ui.tags.link(rel="stylesheet", href="www/style.css")),

    # JavaScript for sidebar toggling behavior
    ui.head_content(
        ui.tags.script("""
            Shiny.addCustomMessageHandler("sidebar_toggled", (message) => {
                const layoutEl = document.querySelector(".bslib-sidebar-layout");
                if (layoutEl) {
                    layoutEl.style.setProperty("grid-template-columns", `${message.width} 1fr`, "important");
                }

                const isCollapsed = message.collapsed;

                /* NEW: push the width into a CSS variable that the stylesheet will pick up */
                document.documentElement.style.setProperty("--sidebar-width", message.width);

                document.querySelectorAll(".nav-pills .nav-link").forEach(linkEl => {
                    if (!linkEl.dataset.origHTML) {
                        linkEl.dataset.origHTML = linkEl.innerHTML;
                    }

                    if (isCollapsed) {
                        const iTag = linkEl.querySelector("i");
                        if (iTag) {
                            linkEl.innerHTML = iTag.outerHTML;
                        }
                    } else {
                        linkEl.innerHTML = linkEl.dataset.origHTML;
                    }
                });

                const btn = document.getElementById("toggle_sidebar");
                if (btn) {
                    btn.style.marginLeft = message.collapsed ? "63px" : "192px";
                }
            });            
        """)
    ),
    ##### WebApp Styling END #####

##### Header Panel START (Do Not Edit) #####
    ui.row(
        ui.div(
            ui.div(
                ui.output_image("app_title_id", height="100%"),
                style="margin: 5px; margin-left:12px;"
            ),
            ui.input_action_button(
                "toggle_sidebar", "", width="34px;", class_="Toggle-Button",
                style="height: 40px; margin-top: -58px; margin-bottom: 0px; margin-left: 192px; border-radius: 0px; padding:0px; padding-top:0px; padding-bottom: 0px; box-shadow: none;",
                icon=ui.tags.i(class_="fa fa-bars")
            ),
            style="height: 38px; overflow: hidden; margin-bottom: -15px; margin-top: -15px; position: relative; z-index: 10; box-shadow: 5px 5px 10px #00000012 !important; background-color: #fff;"
        ), style = "border: 2px #fff !important"
    ),
##### Header Panel END #####
    ui.page_fillable(
        ui.div(                           # <- flex-wrapper
            ui.navset_pill(               #    unchanged nav-set
                ui.nav_panel(ui.HTML('<i class="fas fa-home"></i> Home'),     home_tab_content),
                ui.nav_panel(ui.HTML('<i class="fas fa-cogs"></i> Settings'), settings_tab_content),
                ui.nav_panel(ui.HTML('<i class="fas fa-chart-bar"></i> Reports'), reports_tab_content),
                ui.nav_panel(ui.HTML('<i class="fas fa-comment-dots"></i> Feedback'), feedback_tab_content),
                id="tabs"
            ),
            class_="layout-container"     # <- NEW class, see CSS below
        ),
        ui.row(
            ui.column(6, ui.output_ui("copyright_company_URL_id")),
            ui.column(2, ui.output_text("Version_track_id"), offset=4, style="text-align:right;"),
            style="margin-top: -15px; padding: 10px; background-color: #fff;"
        ) 
    )
    
)

##### Server Definition START  #####
def server(input, output, session):

    ##### Toggle Sidebar Functionality START (Do Not Edit) #####
    # Track the state of the toggled side bar
    toggled = reactive.Value(False)
    
    # Toggle the iAchieve logo between the full and toggled state
    @output
    @render.image
    def app_title_id():
        if toggled.get():
            img_file = resource_dir / "iAchieve_Logo_Only.png"
            width_css = "52px"
        else:
            img_file = resource_dir / "iAchieve_Logo.png"
            width_css = "175px"
        return {"src": img_file, "style": f"width:{width_css}; margin-left: -3px; margin-right: 0px;"}

    # Toggle the sidebar width and toggled button position between the expanded and collapsed state 
    # (also removes tab names and leaves just icons)
    @reactive.Effect
    @reactive.event(input.toggle_sidebar)
    async def _toggle_layout_columns():
        toggled.set(not toggled.get())
        new_width = "55px" if toggled.get() else "185px"
        await session.send_custom_message("sidebar_toggled", {
            "width": new_width,
            "collapsed": toggled.get()
        })

    # Returns the copyright APC and adjusts the position based on the toggled state
    @output
    @render.ui
    def copyright_company_URL_id():
        margin_left = "55px" if toggled.get() else "185px"
        return ui.div(
            ui.HTML("&#169;"),
            ui.span(datetime.now().year),
            ui.span(" "),
            ui.a("APC", href="https://approcess.com/", target="_blank"),
            style=f"margin-left: {margin_left};"
        )
    
    ##### Feedback Submission Logic START (Editable or Remove, as needed) #####
    email_string = reactive.value(None)

    @output
    @render.ui
    def submit_feedback_ui_id():
        return ui.a(
            ui.input_action_button(id="submit_feedback_id", label="Submit Feedback", icon=icon_svg("envelope"), width="100%", class_="Green-Button", style="margin-top: 125px;"),
            href=email_string()
        )

    @reactive.effect
    def _():
        req(input.feedback_type_id() and input.feedback_webapp_name_id() and input.feedback_details_id())
        feedback_type = input.feedback_type_id().replace(" ", "%20")
        WebApp_name = input.feedback_webapp_name_id().replace(" ", "%20")
        feedback_details = input.feedback_details_id().replace(" ", "%20")
        email_string.set(f"mailto:shinyapps@approcess.com?subject={feedback_type}:%20%20{WebApp_name}&body={feedback_details}")
##### Feedback Submission Logic END #####

##### Version Tracking START (Do Not Edit) #####
    @output
    @render.text
    def Version_track_id():
        return Web_app_version
##### Version Tracking END #####


# Add additional server elements as required


    
##### Server Definition END #####




# Set up the app with the ui, server, and point it in the direction of the www folder
app = App(app_ui, server, static_assets={"/www": resource_dir})
# Run the app and launch it in the browser
#app.run(launch_browser=True)