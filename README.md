# TelemXnet
Reliable networks for Unmanned Vehicles

This is a Python3 (no Python 2.X support) library that supports sending data packets over multiple udp links.

A server with a public address is required to act as the middle point.

Typically, TelemXnet-Server will run on the server, with TememXnet-client running on the UAV (or any remote vehicle) and the GCS.

Each UAV-GCS link has a unique 32bit address ID. Thus the server can support many multiple links.

Each client will input/output it's data via a local udp server. Any data put into that port will appear at the other client's output.

After much development, I've discovered that Python (or Linux rather) does not let the user specify which network interface departing packets are routed through. So TelemXnet does not actually run on multiple network interfaces.

