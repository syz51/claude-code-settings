#!/usr/bin/env python3
"""Browser automation CLI using chrome-devtools-mcp via FastMCP client.

NOTE: Many interaction commands (click, fill, hover, etc.) require element UIDs
from a snapshot. Workflow: take-snapshot first, then use UIDs for interactions.
"""

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def call_mcp_tool(tool_name: str, args: dict[str, Any]) -> Any:
    """Spawn chrome-devtools-mcp and call a tool."""
    transport = StdioTransport(command="bunx", args=["chrome-devtools-mcp@latest"])
    async with Client(transport) as client:
        result = await client.call_tool(tool_name, args)
        return result


def run_tool(tool_name: str, args: dict[str, Any], save_path: str | None = None) -> None:
    """Run tool and print JSON result."""
    try:
        result = asyncio.run(call_mcp_tool(tool_name, args))

        # Handle screenshot/snapshot save-path (extract from result)
        if save_path and hasattr(result, "content"):
            for item in result.content:
                if hasattr(item, "data") and hasattr(item, "type") and item.type == "image":
                    img_data = base64.b64decode(item.data)
                    Path(save_path).write_bytes(img_data)
                    print(json.dumps({"saved": save_path, "size_bytes": len(img_data)}))
                    return

        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Browser automation via chrome-devtools-mcp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
NOTE: Interaction commands (click, fill, hover, drag) require element UIDs.
Get UIDs by running 'snapshot' first, then use those UIDs.

Example workflow:
  1. browser.py navigate --url https://example.com
  2. browser.py snapshot  # Get element UIDs
  3. browser.py click <uid-from-snapshot>
""",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # === DEBUG (5) ===
    # screenshot
    p = subparsers.add_parser("screenshot", help="Take screenshot of page")
    p.add_argument("--uid", help="Element UID from snapshot to screenshot")
    p.add_argument("--full-page", action="store_true", help="Capture full page")
    p.add_argument("--format", choices=["png", "jpeg", "webp"], default="png")
    p.add_argument("--quality", type=int, help="Quality 0-100 (jpeg/webp only)")
    p.add_argument("--save-path", help="Path to save screenshot locally")

    # snapshot
    p = subparsers.add_parser("snapshot", help="Get accessibility tree/DOM snapshot with element UIDs")
    p.add_argument("--verbose", action="store_true", help="Include full a11y tree info")
    p.add_argument("--save-path", help="Path to save snapshot")

    # eval
    p = subparsers.add_parser("eval", help="Evaluate JavaScript function in page")
    p.add_argument("function", help="JS function, e.g., '() => document.title'")
    p.add_argument("--args", help="JSON array of {uid} objects to pass as args")

    # list-console
    p = subparsers.add_parser("list-console", help="List console messages")
    p.add_argument("--types", help="Comma-separated: log,error,warn,info,debug,etc.")
    p.add_argument("--page-size", type=int, help="Max messages to return")
    p.add_argument("--page-idx", type=int, help="Page number (0-based)")

    # get-console
    p = subparsers.add_parser("get-console", help="Get console message details")
    p.add_argument("msgid", type=int, help="Message ID from list-console")

    # === NAVIGATION (6) ===
    # navigate
    p = subparsers.add_parser("navigate", help="Navigate page")
    p.add_argument("--url", help="URL to navigate to")
    p.add_argument("--back", action="store_true", help="Go back in history")
    p.add_argument("--forward", action="store_true", help="Go forward in history")
    p.add_argument("--reload", action="store_true", help="Reload page")
    p.add_argument("--ignore-cache", action="store_true", help="Ignore cache on reload")
    p.add_argument("--timeout", type=int, help="Timeout in ms")

    # new-page
    p = subparsers.add_parser("new-page", help="Open new browser page/tab")
    p.add_argument("url", help="URL to open in new page")
    p.add_argument("--timeout", type=int, help="Timeout in ms")

    # select-page
    p = subparsers.add_parser("select-page", help="Switch to page by index")
    p.add_argument("page_idx", type=int, help="Page index from list-pages")
    p.add_argument("--bring-to-front", action="store_true", help="Focus the page")

    # close-page
    p = subparsers.add_parser("close-page", help="Close page by index")
    p.add_argument("page_idx", type=int, help="Page index to close")

    # list-pages
    subparsers.add_parser("list-pages", help="List all open pages/tabs")

    # wait-for
    p = subparsers.add_parser("wait-for", help="Wait for text to appear")
    p.add_argument("text", help="Text to wait for on page")
    p.add_argument("--timeout", type=int, help="Timeout in ms")

    # === INPUT (8) ===
    # click
    p = subparsers.add_parser("click", help="Click element by UID (from snapshot)")
    p.add_argument("uid", help="Element UID from snapshot")
    p.add_argument("--dbl-click", action="store_true", help="Double click")

    # drag
    p = subparsers.add_parser("drag", help="Drag element to another")
    p.add_argument("from_uid", help="Source element UID")
    p.add_argument("to_uid", help="Target element UID")

    # fill
    p = subparsers.add_parser("fill", help="Fill input field by UID")
    p.add_argument("uid", help="Element UID from snapshot")
    p.add_argument("value", help="Value to fill")

    # fill-form
    p = subparsers.add_parser("fill-form", help="Fill multiple form fields")
    p.add_argument("--elements", required=True, help='JSON: [{"uid":"x","value":"y"},...]')

    # handle-dialog
    p = subparsers.add_parser("handle-dialog", help="Handle browser dialog")
    p.add_argument("action", choices=["accept", "dismiss"])
    p.add_argument("--prompt-text", help="Text for prompt dialogs")

    # hover
    p = subparsers.add_parser("hover", help="Hover over element by UID")
    p.add_argument("uid", help="Element UID from snapshot")

    # press-key
    p = subparsers.add_parser("press-key", help="Press keyboard key")
    p.add_argument("key", help="Key with modifiers, e.g., 'Enter', 'Control+A', 'Control+Shift+R'")

    # upload-file
    p = subparsers.add_parser("upload-file", help="Upload file to input by UID")
    p.add_argument("uid", help="File input element UID")
    p.add_argument("file_path", help="Local path to file")

    # === EMULATION (2) ===
    # emulate
    p = subparsers.add_parser("emulate", help="Emulate network/CPU/geolocation")
    p.add_argument(
        "--network",
        choices=["No emulation", "Offline", "Slow 3G", "Fast 3G", "Slow 4G", "Fast 4G"],
        help="Network throttling",
    )
    p.add_argument("--cpu", type=float, help="CPU throttle rate 1-20 (1=no throttle)")
    p.add_argument("--geo", help="Geolocation as 'lat,lon' or 'clear'")

    # resize
    p = subparsers.add_parser("resize", help="Resize viewport")
    p.add_argument("width", type=int, help="Viewport width")
    p.add_argument("height", type=int, help="Viewport height")

    # === NETWORK (2) ===
    # list-network
    p = subparsers.add_parser("list-network", help="List network requests")
    p.add_argument("--types", help="Comma-separated: document,xhr,fetch,script,etc.")
    p.add_argument("--page-size", type=int, help="Max requests to return")
    p.add_argument("--page-idx", type=int, help="Page number (0-based)")

    # get-network
    p = subparsers.add_parser("get-network", help="Get network request details")
    p.add_argument("--reqid", type=int, help="Request ID (omit for selected in DevTools)")

    # === PERFORMANCE (3) ===
    # perf-start
    p = subparsers.add_parser("perf-start", help="Start performance trace")
    p.add_argument("--reload", action="store_true", help="Reload page after starting")
    p.add_argument("--auto-stop", action="store_true", help="Auto-stop recording")

    # perf-stop
    subparsers.add_parser("perf-stop", help="Stop performance trace")

    # perf-analyze
    p = subparsers.add_parser("perf-analyze", help="Analyze performance insight")
    p.add_argument("insight_set_id", help="Insight set ID from trace")
    p.add_argument("insight_name", help="Insight name, e.g., 'DocumentLatency', 'LCPBreakdown'")

    args = parser.parse_args()

    cmd = args.command
    tool_args: dict[str, Any] = {}
    save_path = None

    # === DEBUG ===
    if cmd == "screenshot":
        tool_name = "take_screenshot"
        if args.uid:
            tool_args["uid"] = args.uid
        if args.full_page:
            tool_args["fullPage"] = True
        if args.format != "png":
            tool_args["format"] = args.format
        if args.quality:
            tool_args["quality"] = args.quality
        if args.save_path:
            save_path = args.save_path

    elif cmd == "snapshot":
        tool_name = "take_snapshot"
        if args.verbose:
            tool_args["verbose"] = True
        if args.save_path:
            tool_args["filePath"] = args.save_path

    elif cmd == "eval":
        tool_name = "evaluate_script"
        tool_args["function"] = args.function
        if args.args:
            tool_args["args"] = json.loads(args.args)

    elif cmd == "list-console":
        tool_name = "list_console_messages"
        if args.types:
            tool_args["types"] = args.types.split(",")
        if args.page_size:
            tool_args["pageSize"] = args.page_size
        if args.page_idx is not None:
            tool_args["pageIdx"] = args.page_idx

    elif cmd == "get-console":
        tool_name = "get_console_message"
        tool_args["msgid"] = args.msgid

    # === NAVIGATION ===
    elif cmd == "navigate":
        tool_name = "navigate_page"
        if args.back:
            tool_args["type"] = "back"
        elif args.forward:
            tool_args["type"] = "forward"
        elif args.reload:
            tool_args["type"] = "reload"
            if args.ignore_cache:
                tool_args["ignoreCache"] = True
        elif args.url:
            tool_args["type"] = "url"
            tool_args["url"] = args.url
        else:
            parser.error("navigate requires --url, --back, --forward, or --reload")
        if args.timeout:
            tool_args["timeout"] = args.timeout

    elif cmd == "new-page":
        tool_name = "new_page"
        tool_args["url"] = args.url
        if args.timeout:
            tool_args["timeout"] = args.timeout

    elif cmd == "select-page":
        tool_name = "select_page"
        tool_args["pageIdx"] = args.page_idx
        if args.bring_to_front:
            tool_args["bringToFront"] = True

    elif cmd == "close-page":
        tool_name = "close_page"
        tool_args["pageIdx"] = args.page_idx

    elif cmd == "list-pages":
        tool_name = "list_pages"

    elif cmd == "wait-for":
        tool_name = "wait_for"
        tool_args["text"] = args.text
        if args.timeout:
            tool_args["timeout"] = args.timeout

    # === INPUT ===
    elif cmd == "click":
        tool_name = "click"
        tool_args["uid"] = args.uid
        if args.dbl_click:
            tool_args["dblClick"] = True

    elif cmd == "drag":
        tool_name = "drag"
        tool_args["from_uid"] = args.from_uid
        tool_args["to_uid"] = args.to_uid

    elif cmd == "fill":
        tool_name = "fill"
        tool_args["uid"] = args.uid
        tool_args["value"] = args.value

    elif cmd == "fill-form":
        tool_name = "fill_form"
        tool_args["elements"] = json.loads(args.elements)

    elif cmd == "handle-dialog":
        tool_name = "handle_dialog"
        tool_args["action"] = args.action
        if args.prompt_text:
            tool_args["promptText"] = args.prompt_text

    elif cmd == "hover":
        tool_name = "hover"
        tool_args["uid"] = args.uid

    elif cmd == "press-key":
        tool_name = "press_key"
        tool_args["key"] = args.key

    elif cmd == "upload-file":
        tool_name = "upload_file"
        tool_args["uid"] = args.uid
        tool_args["filePath"] = args.file_path

    # === EMULATION ===
    elif cmd == "emulate":
        tool_name = "emulate"
        if args.network:
            tool_args["networkConditions"] = args.network
        if args.cpu:
            tool_args["cpuThrottlingRate"] = args.cpu
        if args.geo:
            if args.geo == "clear":
                tool_args["geolocation"] = None
            else:
                lat, lon = map(float, args.geo.split(","))
                tool_args["geolocation"] = {"latitude": lat, "longitude": lon}

    elif cmd == "resize":
        tool_name = "resize_page"
        tool_args["width"] = args.width
        tool_args["height"] = args.height

    # === NETWORK ===
    elif cmd == "list-network":
        tool_name = "list_network_requests"
        if args.types:
            tool_args["resourceTypes"] = args.types.split(",")
        if args.page_size:
            tool_args["pageSize"] = args.page_size
        if args.page_idx is not None:
            tool_args["pageIdx"] = args.page_idx

    elif cmd == "get-network":
        tool_name = "get_network_request"
        if args.reqid is not None:
            tool_args["reqid"] = args.reqid

    # === PERFORMANCE ===
    elif cmd == "perf-start":
        tool_name = "performance_start_trace"
        tool_args["reload"] = args.reload
        tool_args["autoStop"] = args.auto_stop

    elif cmd == "perf-stop":
        tool_name = "performance_stop_trace"

    elif cmd == "perf-analyze":
        tool_name = "performance_analyze_insight"
        tool_args["insightSetId"] = args.insight_set_id
        tool_args["insightName"] = args.insight_name

    else:
        parser.error(f"Unknown command: {cmd}")

    run_tool(tool_name, tool_args, save_path=save_path)


if __name__ == "__main__":
    main()
