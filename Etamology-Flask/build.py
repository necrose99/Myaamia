import os

def assemble_applet(output_name="index.html"):
    components = [
        "templates/header.html",
        "static/applet.css",
        "static/kilahkwaani_v2.js",
        "static/bridge.js",
        "templates/footer.html"
    ]
    
    with open(output_name, "w", encoding="utf-8") as f_out:
        for comp in components:
            if os.path.exists(comp):
                with open(comp, "r", encoding="utf-8") as f_in:
                    # Wrap JS and CSS in tags if they aren't already
                    if comp.endswith(".js"):
                        f_out.write("\n<script>\n" + f_in.read() + "\n</script>\n")
                    elif comp.endswith(".css"):
                        f_out.write("\n<style>\n" + f_in.read() + "\n</style>\n")
                    else:
                        f_out.write(f_in.read())
                print(f"✔ Added {comp}")
            else:
                print(f"✘ Missing {comp}")

if __name__ == "__main__":
    assemble_applet()
