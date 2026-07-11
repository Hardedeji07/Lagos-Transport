import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Platform // <-- Added missing Platform import here!
} from 'react-native';

export default function App() {
  const [currentTab, setCurrentTab] = useState('Dashboard');

  const zones = [
    { name: 'Apapa Port Corridor', score: 0.88, level: 'SEVERE', color: '#EF4444' },
    { name: 'Third Mainland Bridge', score: 0.65, level: 'HEAVY', color: '#F59E0B' },
    { name: 'Ikeja Inside Grid', score: 0.32, level: 'STABLE', color: '#10B981' }
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      
      {/* Top Brand Bar */}
      <View style={styles.header}>
        <View>
          <Text style={styles.appTitle}>SmartRoute Lagos</Text>
          <Text style={styles.appSubtitle}>AI Logistics Dispatcher</Text>
        </View>
        <View style={styles.avatar}><Text style={styles.avatarTxt}>AO</Text></View>
      </View>

      {/* Main Core Views Switcher */}
      <ScrollView style={styles.content}>
        {currentTab === 'Dashboard' ? (
          <View>
            <Text style={styles.sectionTitle}>TODAY'S METRICS</Text>
            
            {/* Grid Metrics */}
            <View style={styles.grid}>
              <View style={styles.card}>
                <Text style={styles.cardLabel}>📍 Total Stops</Text>
                <Text style={styles.cardValue}>6 Locations</Text>
              </View>
              <View style={styles.card}>
                <Text style={styles.cardLabel}>🕒 Transit Time</Text>
                <Text style={styles.cardValue}>2h 14m</Text>
              </View>
            </View>

            {/* Live Model Pipeline */}
            <Text style={[styles.sectionTitle, { marginTop: 25 }]}>CONGESTION SCORE PIPELINE</Text>
            {zones.map((zone, i) => (
              <View key={i} style={styles.zoneRow}>
                <View>
                  <Text style={styles.zoneName}>{zone.name}</Text>
                  <Text style={[styles.zoneLevel, { color: zone.color }]}>{zone.level}</Text>
                </View>
                <Text style={styles.zoneScore}>{(zone.score).toFixed(2)}</Text>
              </View>
            ))}
          </View>
        ) : (
          /* Route Timeline View */
          <View style={styles.timelineCard}>
            <Text style={styles.sectionTitle}>DELIVERY TIMELINE</Text>
            <Text style={styles.timelineItem}>🟢 Warehouse Ikeja · Depart 07:00</Text>
            <Text style={styles.timelineItem}>🟡 Oshodi Interchange · ETA 07:51</Text>
            <Text style={styles.timelineItem}>🔴 Balogun Market · ETA 09:14</Text>
          </View>
        )}
      </ScrollView>

      {/* Navigation Tab Bar */}
      <View style={styles.tabBar}>
        <TouchableOpacity style={styles.tab} onPress={() => setCurrentTab('Dashboard')}>
          <Text style={[styles.tabText, currentTab === 'Dashboard' && styles.activeTab]}>📊 Dashboard</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tab} onPress={() => setCurrentTab('Route')}>
          <Text style={[styles.tabText, currentTab === 'Route' && styles.activeTab]}>🌿 Route</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: '#121212', 
    paddingTop: Platform.OS === 'android' ? 40 : 0 
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', padding: 20, borderBottomWidth: 1, borderColor: '#1F1F1F', alignItems: 'center' },
  appTitle: { color: '#FFF', fontSize: 20, fontWeight: 'bold' },
  appSubtitle: { color: '#888', fontSize: 12, marginTop: 2 },
  avatar: { width: 35, height: 35, backgroundColor: '#1E3A8A', borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  avatarTxt: { color: '#3B82F6', fontWeight: 'bold' },
  content: { flex: 1, padding: 20 },
  sectionTitle: { color: '#666', fontSize: 12, fontWeight: 'bold', marginBottom: 15, letterSpacing: 1 },
  grid: { flexDirection: 'row', justifyContent: 'space-between' },
  card: { backgroundColor: '#1F1F1F', width: '48%', padding: 15, borderRadius: 10, minHeight: 80, justifyContent: 'center' },
  timelineCard: { backgroundColor: '#1F1F1F', padding: 20, borderRadius: 10 },
  cardLabel: { color: '#AAA', fontSize: 12, marginBottom: 5 },
  cardValue: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  zoneRow: { backgroundColor: '#1F1F1F', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 15, borderRadius: 10, marginBottom: 12 },
  zoneName: { color: '#FFF', fontSize: 14, fontWeight: '500' },
  zoneLevel: { fontSize: 11, fontWeight: 'bold', marginTop: 2 },
  zoneScore: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  timelineItem: { color: '#FFF', fontSize: 14, marginVertical: 12, paddingLeft: 10 },
  tabBar: { flexDirection: 'row', height: 65, borderTopWidth: 1, borderColor: '#1F1F1F', backgroundColor: '#121212', alignItems: 'center' },
  tab: { flex: 1, justifyContent: 'center', alignItems: 'center', height: '100%' },
  tabText: { color: '#666', fontSize: 14 },
  activeTab: { color: '#10B981', fontWeight: 'bold' }
});