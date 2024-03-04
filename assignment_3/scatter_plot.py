import matplotlib.pyplot as plt

# Data for the three cases
# Case 1: Four concurrent downloads from the same server
case_1_rtt = [12, 12, 12, 12]  # RTT in milliseconds
case_1_throughput = [165095720 / 521, 165842766 / 521, 165458792 / 514, 163235772 / 512]  # Throughput in bytes per second

# Case 2: Downloads from different mirror servers around the world
case_2_rtt = [13, 35, 68, 73, 49, 33, 135, 326, 322]  # RTT in milliseconds
case_2_throughput = [261319130 / 90, 175995832 / 90, 151894552 / 90, 140388568 / 90, 108610702 / 90, 70644690 / 90, 65744938 / 90, 43212876 / 90, 39222524 / 90]  # Throughput in bytes per second

# Case 3: BitTorrent download from multiple peers
case_3_rtt = [40, 36, 100, 68, 31, 33, 122, 146, 74, 66]  # RTT in milliseconds
case_3_throughput = [108851134 / 58, 90435681 / 58, 57971584 / 53, 32000012 / 29, 32557334 / 35, 27199361 / 31, 26329578 / 31, 38834490 / 56, 23571761 / 35, 36252962 / 55]  # Throughput in bytes per second

# Convert throughput to bits per second for plotting
case_1_throughput_bps = [x * 8 for x in case_1_throughput]
case_2_throughput_bps = [x * 8 for x in case_2_throughput]
case_3_throughput_bps = [x * 8 for x in case_3_throughput]

# Plotting
plt.figure(figsize=(10, 6))

# Case 1 plot
plt.scatter(case_1_rtt, case_1_throughput_bps, color='blue', label='Case 1: Same Server')

# Case 2 plot
plt.scatter(case_2_rtt, case_2_throughput_bps, color='red', label='Case 2: Different Servers')

# Case 3 plot
plt.scatter(case_3_rtt, case_3_throughput_bps, color='green', label='Case 3: BitTorrent')

# Labels and Legend
plt.xlabel('RTT (milliseconds)')
plt.ylabel('Throughput (bps)')
plt.title('RTT vs Throughput for Different TCP Scenarios')
plt.legend()

# Show plot
plt.show()
